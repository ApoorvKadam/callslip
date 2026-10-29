variable "kubeconfig_path" {
  description = "Kubeconfig file with access to the cluster."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "Context in that kubeconfig, for example kind-callslip."
  type        = string
}

variable "overlay" {
  description = "Which overlay in deploy/kubernetes/overlays to apply."
  type        = string
  default     = "kind"
  validation {
    condition     = contains(["kind", "ingress", "openshift"], var.overlay)
    error_message = "overlay must be kind, ingress or openshift."
  }
}

variable "namespace" {
  description = "Namespace (OpenShift: project) to deploy into."
  type        = string
  default     = "callslip"
}

variable "create_namespace" {
  description = "Create the namespace. Set false when it already exists, as on OpenShift."
  type        = bool
  default     = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key for the API and the run workers. Without one, asking returns 503."
  type        = string
  sensitive   = true
}

variable "image_registry" {
  description = "Registry and path holding callslip-backend and callslip-frontend. Empty: keep the overlay's."
  type        = string
  default     = ""
}

variable "image_tag" {
  description = "Image tag to deploy, normally the commit's short SHA."
  type        = string
  default     = "dev"
}

variable "route_host" {
  description = "Public host for the OpenShift Routes, under the cluster's application domain."
  type        = string
  default     = ""
}

variable "tls_cert_file" {
  description = "Certificate for the ingress overlays' callslip-tls Secret. Empty: no Secret."
  type        = string
  default     = ""
}

variable "tls_key_file" {
  description = "Private key for that certificate."
  type        = string
  default     = ""
}
