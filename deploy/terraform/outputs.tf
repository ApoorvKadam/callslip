output "namespace" {
  value = var.namespace
}

output "resources" {
  description = "Every resource applied from the overlay."
  value       = sort(keys(data.kustomization_overlay.callslip.manifests))
}
