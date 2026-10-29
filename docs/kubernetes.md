# Kubernetes and OpenShift

The same images that Docker Compose runs, as Kubernetes resources: `deploy/kubernetes/`, built with kustomize (part of `kubectl`).

| Path | What it is |
|---|---|
| `base/` | PostgreSQL (StatefulSet with a 10 GiB volume), Redis, the API, the run workers, the ingestion worker and the frontend, with their Services, probes, resource limits, network policies and a settings ConfigMap |
| `overlays/ingress/` | the base plus an Ingress over TLS: `/api` to the API, everything else to the frontend |
| `overlays/openshift/` | the base plus two Routes on one host, and no fixed user ids (OpenShift assigns them) |
| `overlays/kind/` | the ingress overlay on a local [kind](https://kind.sigs.k8s.io/) cluster: locally built images and one replica of each; `cluster.yaml` makes the cluster |

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
| `FORWARDED_ALLOW_IPS: "*"` (only the frontend proxy reaches the API) | `FORWARDED_ALLOW_IPS: 10.0.0.0/8`, and a network policy in each overlay that lets only the ingress controller or router reach the API. Failed sign-ins are counted per client address, so no other pod may set that address |
| `.env` | ConfigMap `callslip-settings` (non-secret settings) and Secret `callslip-secrets` |
| `mem_limit` with `memswap_limit` (no swap) | the same limits as `resources.limits.memory` |

Every container runs as a non-root user with no added capabilities, no privilege escalation and the default seccomp profile. Network policies let only the API and the two kinds of worker reach PostgreSQL, and only the API and the run workers reach Redis, which has no password of its own. Only the ingress controller (namespace `ingress-nginx`) or the OpenShift router reaches the API. The frontend image is the unprivileged nginx build on port 8080, so it runs under OpenShift's restricted security context unchanged.

## Run it on a local cluster

kind runs a Kubernetes node as a Docker container and enforces network policies. This runs the ingress overlay, with the real ingress controller, TLS and every network policy. It needs kind 0.24 or later and about 3.5 GB of free memory.

```bash
kind create cluster --config deploy/kubernetes/overlays/kind/cluster.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.15.1/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=300s

docker build -t callslip-backend:local backend
docker build -t callslip-frontend:local frontend
kind load docker-image --name callslip callslip-backend:local callslip-frontend:local

kubectl create namespace callslip
openssl req -x509 -newkey rsa:2048 -nodes -days 7 -subj "/CN=callslip.example.edu" \
  -addext "subjectAltName=DNS:callslip.example.edu" -keyout tls.key -out tls.crt
kubectl -n callslip create secret tls callslip-tls --cert=tls.crt --key=tls.key
kubectl -n callslip create secret generic callslip-secrets \
  --from-literal=POSTGRES_PASSWORD="$(openssl rand -hex 24)" \
  --from-literal=ANTHROPIC_API_KEY=...
kubectl apply -k deploy/kubernetes/overlays/kind
kubectl -n callslip rollout status deploy/api

# With "127.0.0.1 callslip.example.edu" in /etc/hosts:
SSL_CERT_FILE=tls.crt python3 scripts/load_corpus.py --base https://callslip.example.edu:8443
```

Then open https://callslip.example.edu:8443 and accept the self-signed certificate. `kind delete cluster --name callslip` removes it all. The ingress-nginx project is retired upstream; it is used here because the overlay's annotations are written for it, and OpenShift uses its own router.

### What the local run showed

Run on 2026-10-28 with kind 0.33 (Kubernetes 1.37) and ingress-nginx 1.15.1. Every request below went through the ingress over TLS. A probe fetched `/api/ready`, `/api/documents` and `/` about ten times a second during each change.

| Check | Result |
|---|---|
| Empty cluster to every pod ready | 25 s. The apps restarted once each while PostgreSQL started, then stayed up |
| The 14 corpus PDFs ingested | 402 s, all ready. The ingestion worker peaked at 609 MiB under its 1 GiB limit |
| The 27-step browser check: ask, cite, compare, export, sign in, private upload and delete, another account, sign-in limit | 27 of 27 pass |
| Network policies, from a pod with no role | API, PostgreSQL and Redis all unreachable |
| Network policies, from a pod labelled as the API | PostgreSQL and Redis reachable; the API itself unreachable (only the ingress controller may call it) |
| Update to a new image | done in 13 s. Without a pause before shutdown, 5 of 1,509 requests failed with 502; with it, 0 of 765 |
| A release whose image cannot be pulled | the old pod kept serving: 0 of 1,017 requests failed. `kubectl rollout undo` took 1 s |
| PostgreSQL pod deleted | back in 3 s on the same volume: 15 documents, 1,294 passages, 3 accounts and 27 runs before and after. 5 requests failed in those 3 s |
| Redis pod deleted | back in 2 s; 0 of 402 requests failed |
| `/metrics` | answers inside the API pod; through the ingress the path returns the web page |

Two fixes came from this run. The ingestion worker was killed for memory in a loop: it embedded 32 passages at a time and reached 1.36 GB, which Compose had hidden by letting it swap. It now embeds 8 at a time. The API and frontend now pause 5 s before stopping, so the ingress stops sending them requests first.

## What is checked, and what is not

- CI renders every overlay and validates every resource against the Kubernetes and OpenShift schemas (kubeconform, strict mode).
- The ingress overlay ran on a local kind cluster (above). The OpenShift overlay is schema-checked only: it has not run on OpenShift.
- The API runs two replicas and rolls out one pod at a time: it queues runs and keeps no run state. Two run workers (`runner`) execute the questions; more can be added the same way.
- For production, PostgreSQL would be the platform's managed service with the `vector` extension, and Redis a managed cache; `DATABASE_URL` and `REDIS_URL` then point at them and the two in-cluster workloads are dropped.
