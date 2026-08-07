# Helm Deployment Guide

This guide provides comprehensive instructions for deploying the Classic Models API using Helm charts on Kubernetes or OpenShift.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Upgrading](#upgrading)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Uninstalling](#uninstalling)
- [Advanced Topics](#advanced-topics)

## 🎯 Overview

The Classic Models API Helm chart provides a production-ready deployment with:

- **MySQL Database**: Chart-managed (Bitnami) or external MySQL support
- **Auto-scaling**: HorizontalPodAutoscaler support
- **Platform Support**: Works on both Kubernetes and OpenShift
- **Security**: Built-in secrets management and security contexts
- **Flexibility**: Extensive configuration options via values
- **External Database**: Connect to existing MySQL databases

### Chart Architecture

```
┌─────────────────────────────────────────┐
│         Helm Release                     │
│  (classic-models-api)                   │
├─────────────────────────────────────────┤
│                                          │
│  ┌────────────────┐  ┌───────────────┐ │
│  │   API Pods     │  │  MySQL Pod    │ │
│  │   (2+ replicas)│  │  (Bitnami)    │ │
│  └────────────────┘  └───────────────┘ │
│         │                    │          │
│  ┌────────────────┐  ┌───────────────┐ │
│  │   Service      │  │  Service      │ │
│  │   (ClusterIP)  │  │  (ClusterIP)  │ │
│  └────────────────┘  └───────────────┘ │
│         │                               │
│  ┌────────────────┐                    │
│  │ Route/Ingress  │                    │
│  │ (External)     │                    │
│  └────────────────┘                    │
│                                          │
│  ConfigMaps, Secrets, PVCs              │
└─────────────────────────────────────────┘
```

## 🔧 Prerequisites

### Required Tools

1. **Helm 3.0+**
   ```bash
   # Install Helm
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   
   # Verify installation
   helm version
   ```

2. **kubectl or oc CLI**
   ```bash
   # Kubernetes
   kubectl version --client
   
   # OpenShift
   oc version
   ```

3. **Access to Cluster**
   ```bash
   # Kubernetes
   kubectl cluster-info
   
   # OpenShift
   oc login <cluster-url>
   ```

### Cluster Requirements

- Kubernetes 1.19+ or OpenShift 4.x+
- PersistentVolume provisioner (for MySQL storage)
- Sufficient resources:
  - **API**: 2 pods × (100m CPU, 256Mi RAM) minimum
  - **MySQL**: 1 pod × (250m CPU, 512Mi RAM) minimum
  - **Storage**: 10Gi for MySQL data

## 🚀 Quick Start

### 1. Add Bitnami Repository

The chart depends on Bitnami's MySQL chart:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2. Install with Default Values

```bash
# Install in a new namespace
helm install classic-models-api ./helm/classic-models-api \
  --create-namespace \
  --namespace classic-models \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### 3. Verify Installation

```bash
# Check release status
helm status classic-models-api -n classic-models

# Check pods
kubectl get pods -n classic-models

# Get access URL (OpenShift)
oc get route classic-models-api -n classic-models -o jsonpath='{.spec.host}'

# Get access URL (Kubernetes with Ingress)
kubectl get ingress classic-models-api -n classic-models
```

## 📦 Installation

### Development Installation

For local development or testing:

```bash
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --set app.debug=true \
  --set replicaCount=1 \
  --set mysql.primary.persistence.size=5Gi \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Production Installation

For production deployments with security and high availability:

```bash
# Generate secure secrets
DJANGO_SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
MYSQL_PASSWORD=$(openssl rand -base64 32)

# Install with production values
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --values helm/classic-models-api/values-production.yaml \
  --set app.secretKey="$DJANGO_SECRET" \
  --set app.allowedHosts="api.example.com,*.example.com" \
  --set mysql.auth.rootPassword="$MYSQL_ROOT_PASSWORD" \
  --set mysql.auth.password="$MYSQL_PASSWORD" \
  --set route.host="classic-models-api.apps.example.com" \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### OpenShift-Specific Installation

```bash
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --set global.openshift=true \
  --set route.enabled=true \
  --set route.host="classic-models-api.apps.your-cluster.example.com" \
  --set route.tls.enabled=true \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Kubernetes-Specific Installation

```bash
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --set global.openshift=false \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=classic-models-api.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Using External MySQL Database

The chart supports connecting to an existing external MySQL database instead of deploying MySQL with the chart. This is useful when:

- You have a managed MySQL service (e.g., AWS RDS, Azure Database for MySQL, Google Cloud SQL)
- You want to use an existing on-premises MySQL server
- You need to share a database across multiple applications
- You prefer to manage MySQL separately from the application

#### Option 1: Using the External MySQL Values File

```bash
# Use the provided external MySQL values file as a template
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --values helm/classic-models-api/values-external-mysql.yaml \
  --set mysql.externalHost="mysql.example.com" \
  --set mysql.auth.password="your-secure-password"
```

#### Option 2: Using Command-Line Overrides

```bash
helm install classic-models-api ./helm/classic-models-api \
  --namespace classic-models \
  --create-namespace \
  --set mysql.enabled=false \
  --set mysql.externalHost="mysql.example.com" \
  --set mysql.externalPort=3306 \
  --set mysql.auth.database="classicmodels" \
  --set mysql.auth.username="classicuser" \
  --set mysql.auth.password="your-password"
```

#### Prerequisites for External MySQL

Before deploying with external MySQL, ensure:

1. **Database exists**: Create the `classicmodels` database on your MySQL server
   ```sql
   CREATE DATABASE classicmodels CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **User has permissions**: Create a user with appropriate permissions
   ```sql
   CREATE USER 'classicuser'@'%' IDENTIFIED BY 'your-password';
   GRANT ALL PRIVILEGES ON classicmodels.* TO 'classicuser'@'%';
   FLUSH PRIVILEGES;
   ```

3. **Schema is initialized**: Run the initialization script
   ```bash
   mysql -h mysql.example.com -u classicuser -p classicmodels < db/mysqlsampledatabase.sql
   ```

4. **Network connectivity**: Ensure the Kubernetes/OpenShift cluster can reach the MySQL server
   - Check firewall rules
   - Verify security groups (for cloud providers)
   - Test connectivity: `kubectl run -it --rm mysql-test --image=mysql:8 --restart=Never -- mysql -h mysql.example.com -u classicuser -p`

5. **DNS resolution**: The hostname must be resolvable from within the cluster
   - For external hostnames, ensure DNS is configured
   - For internal services, use the full service name (e.g., `mysql.database.svc.cluster.local`)

## ⚙️ Configuration

### Using Custom Values Files

Create a custom values file:

```yaml
# my-values.yaml
app:
  debug: false
  secretKey: "your-secure-secret-key"
  allowedHosts: "api.example.com"

replicaCount: 3

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10

mysql:
  auth:
    rootPassword: "secure-root-password"
    password: "secure-user-password"
  primary:
    persistence:
      size: 50Gi
```

Install with custom values:

```bash
helm install classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Key Configuration Parameters

#### Application Settings

```bash
# Django debug mode
--set app.debug=false

# API version
--set app.apiVersion="1.0.0"

# Allowed hosts
--set app.allowedHosts="api.example.com,*.example.com"

# Django secret key
--set app.secretKey="your-secret-key"

# Optional API key
--set app.apiKey="your-api-key"
```

#### Scaling Settings

```bash
# Number of replicas
--set replicaCount=3

# Enable autoscaling
--set autoscaling.enabled=true
--set autoscaling.minReplicas=3
--set autoscaling.maxReplicas=10
--set autoscaling.targetCPUUtilizationPercentage=70
```

#### Resource Settings

```bash
# CPU and memory limits
--set resources.limits.cpu=1000m
--set resources.limits.memory=1Gi
--set resources.requests.cpu=200m
--set resources.requests.memory=512Mi
```

#### MySQL Settings

```bash
# MySQL credentials
--set mysql.auth.rootPassword="root-password"
--set mysql.auth.database="classicmodels"
--set mysql.auth.username="classicuser"
--set mysql.auth.password="user-password"

# Storage size
--set mysql.primary.persistence.size=50Gi

# Storage class
--set mysql.primary.persistence.storageClass="fast-ssd"
```

#### Route/Ingress Settings

```bash
# OpenShift Route
--set route.enabled=true
--set route.host="api.apps.example.com"
--set route.tls.enabled=true

# Kubernetes Ingress
--set ingress.enabled=true
--set ingress.className=nginx
--set ingress.hosts[0].host=api.example.com
```

### Environment-Specific Values

The chart includes pre-configured values files:

- **`values.yaml`**: Default development values
- **`values-production.yaml`**: Production-ready configuration

Use them as templates:

```bash
# Copy and customize
cp helm/classic-models-api/values-production.yaml my-production-values.yaml

# Edit with your values
vim my-production-values.yaml

# Install
helm install classic-models-api ./helm/classic-models-api \
  -f my-production-values.yaml \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

## 🔄 Upgrading

### Upgrade with New Values

```bash
# Upgrade with new configuration
helm upgrade classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  --namespace classic-models
```

### Upgrade Application Version

```bash
# Upgrade to new image version
helm upgrade classic-models-api ./helm/classic-models-api \
  --set image.tag=2.0.0 \
  --namespace classic-models
```

### Upgrade with Rollback Support

```bash
# Upgrade with automatic rollback on failure
helm upgrade classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  --atomic \
  --timeout 10m \
  --namespace classic-models
```

### View Upgrade History

```bash
# List all revisions
helm history classic-models-api -n classic-models

# Rollback to previous version
helm rollback classic-models-api -n classic-models

# Rollback to specific revision
helm rollback classic-models-api 2 -n classic-models
```

## 📊 Monitoring

### Check Release Status

```bash
# Get release information
helm status classic-models-api -n classic-models

# List all releases
helm list -n classic-models

# Get release values
helm get values classic-models-api -n classic-models

# Get all release information
helm get all classic-models-api -n classic-models
```

### Monitor Pods

```bash
# Watch pod status
kubectl get pods -n classic-models -w

# Check pod details
kubectl describe pod <pod-name> -n classic-models

# View pod logs
kubectl logs -f deployment/classic-models-api -n classic-models

# View MySQL logs
kubectl logs -f deployment/classic-models-api-mysql -n classic-models
```

### Check Resources

```bash
# View all resources
kubectl get all -n classic-models

# Check services
kubectl get svc -n classic-models

# Check routes (OpenShift)
oc get route -n classic-models

# Check ingress (Kubernetes)
kubectl get ingress -n classic-models

# Check PVCs
kubectl get pvc -n classic-models
```

### Access Application

```bash
# Port forward to local machine
kubectl port-forward svc/classic-models-api 8000:8000 -n classic-models

# Access API
curl http://localhost:8000/classic-models/api/v1/

# View API documentation
open http://localhost:8000/classic-models/api/docs/
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
kubectl get pods -n classic-models

# Describe pod for events
kubectl describe pod <pod-name> -n classic-models

# Check logs
kubectl logs <pod-name> -n classic-models

# Common causes:
# - Image pull errors
# - Resource constraints
# - Configuration errors
```

#### 2. MySQL Connection Errors

```bash
# Check MySQL pod
kubectl get pod -l app.kubernetes.io/name=mysql -n classic-models

# Check MySQL logs
kubectl logs -l app.kubernetes.io/name=mysql -n classic-models

# Test connection from API pod
kubectl exec -it deployment/classic-models-api -n classic-models -- \
  nc -zv classic-models-api-mysql 3306

# Verify secrets
kubectl get secret classic-models-api -n classic-models -o yaml
```

#### 3. Route/Ingress Not Working

```bash
# OpenShift: Check route
oc get route classic-models-api -n classic-models -o yaml

# Kubernetes: Check ingress
kubectl get ingress classic-models-api -n classic-models -o yaml

# Check service endpoints
kubectl get endpoints classic-models-api -n classic-models

# Test service internally
kubectl run -it --rm debug --image=busybox --restart=Never -n classic-models -- \
  wget -O- http://classic-models-api:8000/classic-models/api/v1/
```

#### 4. Helm Installation Failures

```bash
# Dry run to check for errors
helm install classic-models-api ./helm/classic-models-api \
  --dry-run --debug \
  -f my-values.yaml

# Validate chart
helm lint ./helm/classic-models-api

# Check chart dependencies
helm dependency list ./helm/classic-models-api

# Update dependencies
helm dependency update ./helm/classic-models-api
```

#### 5. Resource Quota Issues

```bash
# Check resource quotas
kubectl get resourcequota -n classic-models

# Check limit ranges
kubectl get limitrange -n classic-models

# View resource usage
kubectl top pods -n classic-models
kubectl top nodes
```

### Debug Commands

```bash
# Get all events
kubectl get events -n classic-models --sort-by='.lastTimestamp'

# Describe deployment
kubectl describe deployment classic-models-api -n classic-models

# Check HPA status (if enabled)
kubectl get hpa -n classic-models
kubectl describe hpa classic-models-api -n classic-models

# Execute shell in pod
kubectl exec -it deployment/classic-models-api -n classic-models -- /bin/bash

# Check environment variables
kubectl exec deployment/classic-models-api -n classic-models -- env | sort
```

## 🧹 Uninstalling

### Remove Release

```bash
# Uninstall release (keeps PVCs)
helm uninstall classic-models-api -n classic-models

# Delete PVCs manually if needed
kubectl delete pvc -l app.kubernetes.io/instance=classic-models-api -n classic-models

# Delete namespace (removes everything)
kubectl delete namespace classic-models
```

### Clean Uninstall

```bash
# Remove everything including PVCs
helm uninstall classic-models-api -n classic-models
kubectl delete pvc --all -n classic-models
kubectl delete namespace classic-models
```

## 🎓 Advanced Topics

### Using Helm Secrets

For managing sensitive data:

```bash
# Install helm-secrets plugin
helm plugin install https://github.com/jkroepke/helm-secrets

# Create encrypted secrets file
cat > secrets.yaml <<EOF
app:
  secretKey: "my-secret-key"
mysql:
  auth:
    rootPassword: "root-password"
    password: "user-password"
EOF

# Encrypt the file
helm secrets enc secrets.yaml

# Install with encrypted secrets
helm secrets install classic-models-api ./helm/classic-models-api \
  -f secrets.yaml \
  --namespace classic-models
```

### GitOps with ArgoCD

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: classic-models-api
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/classic-models-api.git
    targetRevision: main
    path: helm/classic-models-api
    helm:
      valueFiles:
      - values-production.yaml
      parameters:
      - name: app.secretKey
        value: $SECRET_KEY
      - name: mysql.auth.password
        value: $MYSQL_PASSWORD
  destination:
    server: https://kubernetes.default.svc
    namespace: classic-models
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### Multi-Environment Deployments

```bash
# Development
helm install classic-models-api-dev ./helm/classic-models-api \
  -f values-dev.yaml \
  --namespace dev

# Staging
helm install classic-models-api-staging ./helm/classic-models-api \
  -f values-staging.yaml \
  --namespace staging

# Production
helm install classic-models-api-prod ./helm/classic-models-api \
  -f values-production.yaml \
  --namespace production
```

### Backup and Restore

```bash
# Backup MySQL data
kubectl exec deployment/classic-models-api-mysql -n classic-models -- \
  mysqldump -u root -p$MYSQL_ROOT_PASSWORD classicmodels > backup.sql

# Restore MySQL data
kubectl exec -i deployment/classic-models-api-mysql -n classic-models -- \
  mysql -u root -p$MYSQL_ROOT_PASSWORD classicmodels < backup.sql
```

### Custom Resource Definitions

For advanced monitoring and management, consider:

- **Prometheus Operator**: For metrics collection
- **Grafana**: For visualization
- **Velero**: For backup and disaster recovery
- **Cert-Manager**: For automatic TLS certificate management

## 📚 Additional Resources

### Documentation

- [Helm Chart README](helm/classic-models-api/README.md) - Detailed chart documentation
- [OpenShift Deployment](OPENSHIFT_DEPLOYMENT.md) - OpenShift-specific guide
- [Main README](README.md) - Project overview
- [Bitnami MySQL Chart](https://github.com/bitnami/charts/tree/main/bitnami/mysql) - MySQL dependency docs

### Helm Resources

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Helm Template Guide](https://helm.sh/docs/chart_template_guide/)

### Kubernetes/OpenShift Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [OpenShift Documentation](https://docs.openshift.com/)

## 🆘 Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Helm chart logs: `helm status classic-models-api -n classic-models`
3. Check application logs: `kubectl logs -f deployment/classic-models-api -n classic-models`
4. Consult the [Helm Chart README](helm/classic-models-api/README.md)
5. Review [OpenShift Deployment Guide](OPENSHIFT_DEPLOYMENT.md) for platform-specific issues