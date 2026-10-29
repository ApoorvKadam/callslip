# Deploys Callslip to an existing cluster from the same Kustomize overlays that kubectl applies.
# Terraform adds what the overlays leave out: the namespace and the two Secrets, with a generated
# database password. The state file then holds those secrets, so it stays out of git. Steps: docs/kubernetes.md#apply-with-terraform.

terraform {
  required_version = ">= 1.6"
  required_providers {
    kustomization = {
      source  = "kbst/kustomization"
      version = "~> 0.9.8"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.7"
    }
  }
}

provider "kustomization" {
  kubeconfig_path = var.kubeconfig_path
  context         = var.kube_context
}

resource "random_password" "postgres" {
  length  = 32
  special = false
}

# On OpenShift the project already exists and users may not create namespaces.
resource "kustomization_resource" "namespace" {
  count = var.create_namespace ? 1 : 0
  manifest = jsonencode({
    apiVersion = "v1"
    kind       = "Namespace"
    metadata   = { name = var.namespace }
  })
}

# The workloads read their Secrets by these fixed names. The Secrets are separate resources so the
# overlay holds no value known only at apply time; Terraform can then list its resources at plan.
resource "kustomization_resource" "secrets" {
  manifest = sensitive(jsonencode({
    apiVersion = "v1"
    kind       = "Secret"
    metadata   = { name = "callslip-secrets", namespace = var.namespace }
    type       = "Opaque"
    data = {
      POSTGRES_PASSWORD = base64encode(random_password.postgres.result)
      ANTHROPIC_API_KEY = base64encode(var.anthropic_api_key)
    }
  }))
  depends_on = [kustomization_resource.namespace]
}

# The ingress overlays serve TLS from callslip-tls; OpenShift's router has its own certificate.
resource "kustomization_resource" "tls" {
  count = var.tls_cert_file == "" ? 0 : 1
  manifest = sensitive(jsonencode({
    apiVersion = "v1"
    kind       = "Secret"
    metadata   = { name = "callslip-tls", namespace = var.namespace }
    type       = "kubernetes.io/tls"
    data = {
      "tls.crt" = filebase64(var.tls_cert_file)
      "tls.key" = filebase64(var.tls_key_file)
    }
  }))
  depends_on = [kustomization_resource.namespace]
}

data "kustomization_overlay" "callslip" {
  resources = ["${path.module}/../kubernetes/overlays/${var.overlay}"]
  namespace = var.namespace
}

locals {
  manifests = data.kustomization_overlay.callslip.manifests
}

# Applied in kustomize's priority order: namespaces and CRDs, then everything else, then webhooks.
resource "kustomization_resource" "p0" {
  for_each   = data.kustomization_overlay.callslip.ids_prio[0]
  manifest   = local.manifests[each.value]
  depends_on = [kustomization_resource.namespace]
}

resource "kustomization_resource" "p1" {
  for_each = data.kustomization_overlay.callslip.ids_prio[1]
  manifest = local.manifests[each.value]
  # Wait for Deployments and the StatefulSet to be ready, so a bad release fails the apply.
  wait = true
  timeouts {
    create = "10m"
    update = "10m"
  }
  depends_on = [kustomization_resource.p0, kustomization_resource.secrets, kustomization_resource.tls]
}

resource "kustomization_resource" "p2" {
  for_each   = data.kustomization_overlay.callslip.ids_prio[2]
  manifest   = local.manifests[each.value]
  depends_on = [kustomization_resource.p1]
}
