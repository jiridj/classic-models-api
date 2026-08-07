# Classic Models API Helm Chart

A Helm chart for deploying the Classic Models API (Django REST Framework application) with MySQL database on Kubernetes/OpenShift.

## Features

- 🚀 **Production-ready** Django REST API deployment
- 🗄️ **MySQL database** using Bitnami MySQL chart as dependency
- 🔄 **Auto-scaling** support with HorizontalPodAutoscaler
- 🔐 **Secure** secrets management
- 🌐 **OpenShift Route** or Kubernetes Ingress support
- 📊 **Health checks** with liveness and readiness probes
- 🎯 **Configurable** via values.yaml

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.x+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (for MySQL persistence)

## Installing the Chart

### Add Bitnami Repository (Required for MySQL dependency)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Install with Default Values

```bash
# Install in current namespace
helm install classic-models-api ./helm/classic-models-api

# Install in specific namespace
helm install classic-models-api ./helm/classic-models-api -n classic-models --create-namespace
```

### Install with Custom Values

```bash
# Create a custom values file
cat > my-values.yaml <<EOF
app:
  secretKey: "your-secure-django-secret-key"
  allowedHosts: "api.example.com,*.example.com"

mysql:
  auth:
    rootPassword: "secure-root-password"
    password: "secure-user-password"

route:
  enabled: true
  host: "classic-models-api.apps.example.com"
EOF

# Install with custom values
helm install classic-models-api ./helm/classic-models-api -f my-values.yaml
```

### Install with MySQL Initialization Script

```bash
# Install with database initialization
helm install classic-models-api ./helm/classic-models-api \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Install with External MySQL Database

To use an existing external MySQL database instead of deploying MySQL with the chart:

```bash
# Using the external MySQL values file
helm install classic-models-api ./helm/classic-models-api \
  -f helm/classic-models-api/values-external-mysql.yaml \
  --set mysql.externalHost=mysql.example.com \
  --set mysql.auth.password=your-secure-password

# Or using command-line overrides
helm install classic-models-api ./helm/classic-models-api \
  --set mysql.enabled=false \
  --set mysql.externalHost=mysql.example.com \
  --set mysql.externalPort=3306 \
  --set mysql.auth.database=classicmodels \
  --set mysql.auth.username=classicuser \
  --set mysql.auth.password=your-secure-password
```

**Important Notes for External MySQL:**
- The external MySQL server must be accessible from the Kubernetes/OpenShift cluster
- You must create the database and user with appropriate permissions beforehand
- You are responsible for initializing the database schema (run `db/mysqlsampledatabase.sql`)
- Network connectivity and firewall rules must allow connections from the cluster
- Backups and high availability are your responsibility

## Uninstalling the Chart

```bash
helm uninstall classic-models-api
```

This removes all the Kubernetes/OpenShift components associated with the chart and deletes the release.

## Configuration

The following table lists the configurable parameters of the Classic Models API chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.openshift` | Set to true if deploying on OpenShift | `true` |

### Application Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of API replicas | `2` |
| `image.repository` | API image repository | `classic-models-api` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `image.tag` | Image tag (overrides chart appVersion) | `""` |
| `app.debug` | Enable Django debug mode | `false` |
| `app.apiVersion` | API version | `"1.0.0"` |
| `app.secretKey` | Django secret key | `"change-me-in-production"` |
| `app.apiKey` | Optional API key for system access | `""` |
| `app.allowedHosts` | Allowed hosts (comma-separated) | `"*"` |

### Service Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `service.targetPort` | Container port | `8000` |

### Route Parameters (OpenShift)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `route.enabled` | Enable OpenShift Route | `true` |
| `route.host` | Route hostname (auto-generated if empty) | `""` |
| `route.path` | Route path | `/` |
| `route.tls.enabled` | Enable TLS | `true` |
| `route.tls.termination` | TLS termination type | `edge` |

### Ingress Parameters (Kubernetes)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable Ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts` | Ingress hosts configuration | See values.yaml |

### Resource Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `256Mi` |

### Autoscaling Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `2` |
| `autoscaling.maxReplicas` | Maximum replicas | `5` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

### MySQL Parameters

The chart supports two MySQL deployment modes:

1. **Chart-managed MySQL** (default): Deploys MySQL using the Bitnami MySQL chart
2. **External MySQL**: Connects to an existing external MySQL database

#### Common MySQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mysql.enabled` | Enable chart-managed MySQL (set to false for external) | `true` |
| `mysql.auth.database` | Database name | `"classicmodels"` |
| `mysql.auth.username` | Database username | `"classicuser"` |
| `mysql.auth.password` | Database password | `"classicpass"` |

#### External MySQL Parameters (when mysql.enabled is false)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mysql.externalHost` | External MySQL hostname or IP (required) | `""` |
| `mysql.externalPort` | External MySQL port | `3306` |

#### Chart-managed MySQL Parameters (when mysql.enabled is true)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mysql.enabled` | Enable MySQL deployment | `true` |
| `mysql.auth.rootPassword` | MySQL root password | `"rootpassword"` |
| `mysql.auth.database` | Database name | `"classicmodels"` |
| `mysql.auth.username` | Database user | `"classicuser"` |
| `mysql.auth.password` | Database password | `"classicpass"` |
| `mysql.primary.persistence.enabled` | Enable persistence | `true` |
| `mysql.primary.persistence.size` | PVC size | `10Gi` |

For complete MySQL configuration options, see the [Bitnami MySQL chart documentation](https://github.com/bitnami/charts/tree/main/bitnami/mysql).

## Examples

### Example 1: Production Deployment on OpenShift

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set global.openshift=true \
  --set app.debug=false \
  --set app.secretKey="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
  --set app.allowedHosts="api.example.com" \
  --set mysql.auth.rootPassword="$(openssl rand -base64 32)" \
  --set mysql.auth.password="$(openssl rand -base64 32)" \
  --set route.host="classic-models-api.apps.example.com" \
  --set autoscaling.enabled=true \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Example 2: Development Deployment on Kubernetes

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set global.openshift=false \
  --set app.debug=true \
  --set replicaCount=1 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=classic-models-api.local \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Example 3: Using External MySQL Database

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set mysql.enabled=false \
  --set mysql.externalHost="mysql.example.com" \
  --set mysql.externalPort=3306 \
  --set mysql.auth.database="classicmodels" \
  --set mysql.auth.username="classicuser" \
  --set mysql.auth.password="secure-password"
```

### Example 4: High Availability Setup

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10 \
  --set resources.requests.cpu=200m \
  --set resources.requests.memory=512Mi \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set mysql.primary.persistence.size=50Gi \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

## Upgrading

### Upgrade with New Values

```bash
helm upgrade classic-models-api ./helm/classic-models-api \
  -f my-values.yaml
```

### Upgrade with New Image Version

```bash
helm upgrade classic-models-api ./helm/classic-models-api \
  --set image.tag=2.0.0
```

## Accessing the Application

### On OpenShift (with Route)

```bash
# Get the route URL
export ROUTE_URL=$(oc get route classic-models-api -o jsonpath='{.spec.host}')

# Access the API
curl https://$ROUTE_URL/classic-models/api/v1/

# View API documentation
open https://$ROUTE_URL/classic-models/api/docs/
```

### On Kubernetes (with Ingress)

```bash
# Get the ingress host
export INGRESS_HOST=$(kubectl get ingress classic-models-api -o jsonpath='{.spec.rules[0].host}')

# Access the API
curl http://$INGRESS_HOST/classic-models/api/v1/
```

### Port Forwarding (Development)

```bash
# Forward local port to service
kubectl port-forward svc/classic-models-api 8000:8000

# Access locally
curl http://localhost:8000/classic-models/api/v1/
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=classic-models-api
```

### View Logs

```bash
# API logs
kubectl logs -l app.kubernetes.io/name=classic-models-api -f

# MySQL logs
kubectl logs -l app.kubernetes.io/name=mysql -f
```

### Debug Pod Issues

```bash
# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Execute shell in pod
kubectl exec -it <pod-name> -- /bin/bash
```

### Common Issues

#### 1. MySQL Connection Errors

Check if MySQL is ready:
```bash
kubectl get pods -l app.kubernetes.io/name=mysql
kubectl logs -l app.kubernetes.io/name=mysql
```

#### 2. Image Pull Errors

Verify image exists and pull secrets are configured:
```bash
kubectl describe pod <pod-name> | grep -A 5 "Events:"
```

#### 3. Route/Ingress Not Working

Check route/ingress configuration:
```bash
# OpenShift
oc get route classic-models-api -o yaml

# Kubernetes
kubectl get ingress classic-models-api -o yaml
```

## Development

### Testing the Chart Locally

```bash
# Lint the chart
helm lint ./helm/classic-models-api

# Dry run to see generated manifests
helm install classic-models-api ./helm/classic-models-api --dry-run --debug

# Template the chart
helm template classic-models-api ./helm/classic-models-api > output.yaml
```

### Packaging the Chart

```bash
# Package the chart
helm package ./helm/classic-models-api

# This creates: classic-models-api-1.0.0.tgz
```

## Contributing

Contributions are welcome! Please ensure:
1. Chart passes `helm lint`
2. All templates render correctly with `helm template`
3. Documentation is updated for new parameters

## License

This chart is for educational and demonstration purposes.

## Support

For issues or questions:
- Check the [main documentation](../../README.md)
- Review [OpenShift deployment guide](../../OPENSHIFT_DEPLOYMENT.md)
- Consult [Bitnami MySQL chart docs](https://github.com/bitnami/charts/tree/main/bitnami/mysql)