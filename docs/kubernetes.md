# Kubernetes and OpenShift

The same images that Docker Compose runs, as Kubernetes resources: `deploy/kubernetes/`, built with kustomize (part of `kubectl`).

| Path | What it is |
|---|---|
| `base/` | PostgreSQL (StatefulSet with a 10 GiB volume), Redis, the API, the run workers, the ingestion worker and the frontend, with their Services, probes, resource limits, network policies and a settings ConfigMap |
| `overlays/ingress/` | the base plus an Ingress over TLS: `/api` to the API, everything else to the frontend |
| `overlays/openshift/` | the base plus two Routes on one host, and no fixed user ids (OpenShift assigns them) |

## Deploy

```bash
# 1. Build and push the two images to a registry the cluster can pull from.
docker build -t registry.example.edu/callslip-backend:$(git rev-parse --short HEAD) backend
docker build -t registry.example.edu/callslip-frontend:$(git rev-parse --short HEAD) frontend
docker push registry.example.edu/callslip-backend:$(git rev-parse --short HEAD)
docker push registry.example.edu/callslip-frontend:$(git rev-parse --short HEAD)

# 2. Point the manifests at them: edit the `images` entries in base/kustomization.yaml, or
#    with the standalone kustomize CLI:
cd deploy/kubernetes/base
kustomize edit set image \
  callslip-backend=registry.example.edu/callslip-backend:<sha> \
  callslip-frontend=registry.example.edu/callslip-frontend:<sha>
cd ../overlays/openshift                      # or ../overlays/ingress

# 3. One Secret with two keys, created once per namespace and never committed.
kubectl create secret generic callslip-secrets \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -hex 24)" \
  --from-literal=ANTHROPIC_API_KEY=...

# 4. Apply, then load the corpus through the route or ingress host.
kubectl apply -k .
python3 scripts/load_corpus.py --base https://callslip.apps.example.edu
```

On OpenShift, replace `callslip.apps.example.edu` in `routes.yaml` with the cluster's application domain; the router terminates TLS. With the ingress overlay, replace `callslip.example.edu` in `ingress.yaml` and create the `callslip-tls` certificate Secret, or let cert-manager issue it.

## How it maps from Compose

| Compose | Kubernetes |
|---|---|
| `postgres` with the `pgdata` volume, `pg_isready` health check | StatefulSet with a volume claim; the same check as readiness and liveness probes |
| `redis` with no persistence | Deployment, same arguments; losing the pod costs only cache misses |
| `api`, health check on `/api/health` | Deployment of 2; readiness on `/api/ready` (fails without the database, stays ready without Redis), liveness and startup on `/api/health` |
| `runner`, heartbeat file check | Deployment of 2; the same heartbeat check as a liveness probe |
| `worker`, heartbeat file check | Deployment; the same heartbeat check as a liveness probe |
| `frontend` (nginx, also proxying `/api`) | Deployment of 2; the Ingress or Route sends `/api` straight to the API |
| `FORWARDED_ALLOW_IPS: "*"` (only the frontend proxy reaches the API) | `FORWARDED_ALLOW_IPS: 10.0.0.0/8`: X-Forwarded-For is trusted only from the cluster network, where the ingress or router runs. Set it to that network; failed sign-ins are counted per client address |
| `.env` | ConfigMap `callslip-settings` (non-secret settings) and Secret `callslip-secrets` |
| `mem_limit` | the same limits as `resources.limits.memory` |

Every container runs as a non-root user with no added capabilities, no privilege escalation and the default seccomp profile. Network policies let only the API and the two kinds of worker reach PostgreSQL, and only the API and the run workers reach Redis, which has no password of its own. The frontend image is the unprivileged nginx build on port 8080, so it runs under OpenShift's restricted security context unchanged.

## What is checked, and what is not

- CI renders both overlays and validates every resource against the Kubernetes and OpenShift schemas (kubeconform, strict mode).
- The manifests have not been run on a cluster for this submission. Compose is the tested path (see the [runbook](runbook.md)).
- The API runs two replicas and rolls out one pod at a time: it queues runs and keeps no run state. Two run workers (`runner`) execute the questions; more can be added the same way.
- For production, PostgreSQL would be the platform's managed service with the `vector` extension, and Redis a managed cache; `DATABASE_URL` and `REDIS_URL` then point at them and the two in-cluster workloads are dropped.
