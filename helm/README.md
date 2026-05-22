# Helm Deployment Files

This directory contains Helm charts and helper scripts for deploying the Classic Models API.

## 📁 Contents

- **[`classic-models-api/`](classic-models-api/)** - Main Helm chart
- **[`install-with-db.sh`](install-with-db.sh)** - Helper script for easy installation with database initialization

## 🚀 Quick Start

### Option 1: Using Helper Script (Easiest)

The helper script automatically handles the SQL file injection:

```bash
# Basic installation
./helm/install-with-db.sh

# With custom values
./helm/install-with-db.sh -f my-values.yaml

# Production installation
./helm/install-with-db.sh -n production -f helm/classic-models-api/values-production.yaml

# See all options
./helm/install-with-db.sh --help
```

### Option 2: Direct Helm Command

```bash
# Add Bitnami repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install with SQL file
helm install classic-models-api ./helm/classic-models-api \
  --create-namespace \
  --namespace classic-models \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

## 📖 Passing the MySQL Initialization Script

There are **three ways** to pass the `mysqlsampledatabase.sql` file without hardcoding it:

### Method 1: Using `--set-file` (Recommended)

This is the cleanest approach:

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

**Advantages:**
- ✅ No hardcoding in values files
- ✅ File content automatically injected
- ✅ Works with any file size
- ✅ Clean and maintainable

### Method 2: Using Pre-created ConfigMap

Create a ConfigMap first, then reference it:

```bash
# Create ConfigMap from SQL file
kubectl create configmap mysql-init-script \
  --from-file=01-init.sql=db/mysqlsampledatabase.sql \
  -n classic-models

# Install chart referencing the ConfigMap
helm install classic-models-api ./helm/classic-models-api \
  --set mysql.initdbScriptsConfigMap=mysql-init-script \
  -n classic-models
```

**Advantages:**
- ✅ Good for very large files
- ✅ ConfigMap can be managed separately
- ✅ Can be reused across multiple releases

### Method 3: Using Separate Values File

Generate a values file with the SQL content:

```bash
# Create values file with SQL content
cat > mysql-init-values.yaml <<EOF
mysql:
  initdbScripts:
    01-init.sql: |
$(cat db/mysqlsampledatabase.sql | sed 's/^/      /')
EOF

# Install with multiple values files
helm install classic-models-api ./helm/classic-models-api \
  -f helm/classic-models-api/values.yaml \
  -f mysql-init-values.yaml
```

**Advantages:**
- ✅ Values file can be version controlled (if desired)
- ✅ Can combine with other custom values

**Disadvantages:**
- ❌ Creates a large values file
- ❌ Not ideal for very large SQL files

## 🛠️ Helper Script Usage

The [`install-with-db.sh`](install-with-db.sh) script simplifies installation:

```bash
# Basic usage
./helm/install-with-db.sh

# Custom namespace
./helm/install-with-db.sh -n production

# With custom values file
./helm/install-with-db.sh -f my-values.yaml

# Custom SQL file location
./helm/install-with-db.sh -s /path/to/custom-init.sql

# Dry run to see what would be installed
./helm/install-with-db.sh --dry-run --debug

# Production deployment
./helm/install-with-db.sh \
  -n production \
  -f helm/classic-models-api/values-production.yaml
```

### Script Options

```
OPTIONS:
    -r, --release NAME          Release name (default: classic-models-api)
    -n, --namespace NAMESPACE   Kubernetes namespace (default: classic-models)
    -f, --values FILE           Additional values file
    -s, --sql-file FILE         SQL initialization file (default: ./db/mysqlsampledatabase.sql)
    --no-create-namespace       Don't create namespace if it doesn't exist
    --dry-run                   Perform a dry run
    --debug                     Enable debug output
    -h, --help                  Display this help message
```

## 📚 Documentation

For complete documentation, see:

- **[Chart README](classic-models-api/README.md)** - Detailed chart documentation
- **[HELM_DEPLOYMENT.md](../HELM_DEPLOYMENT.md)** - Comprehensive deployment guide
- **[values.yaml](classic-models-api/values.yaml)** - All configuration options
- **[values-production.yaml](classic-models-api/values-production.yaml)** - Production template

## 🔍 Examples

### Development Installation

```bash
./helm/install-with-db.sh \
  -n dev \
  -f helm/classic-models-api/values.yaml
```

### Production Installation with Secrets

```bash
# Generate secure secrets
DJANGO_SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
MYSQL_PASSWORD=$(openssl rand -base64 32)

# Install with production values and secrets
helm install classic-models-api ./helm/classic-models-api \
  -n production \
  --create-namespace \
  -f helm/classic-models-api/values-production.yaml \
  --set app.secretKey="$DJANGO_SECRET" \
  --set app.allowedHosts="api.example.com" \
  --set mysql.auth.rootPassword="$MYSQL_ROOT_PASSWORD" \
  --set mysql.auth.password="$MYSQL_PASSWORD" \
  --set route.host="api.apps.example.com" \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql
```

### Using External MySQL

```bash
helm install classic-models-api ./helm/classic-models-api \
  --set mysql.enabled=false \
  --set mysql.externalHost="mysql.example.com" \
  --set mysql.externalPort=3306 \
  --set mysql.auth.database="classicmodels" \
  --set mysql.auth.username="classicuser" \
  --set mysql.auth.password="secure-password"
```

## 🔄 Upgrading

```bash
# Upgrade with new values
helm upgrade classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql

# Upgrade to new version
helm upgrade classic-models-api ./helm/classic-models-api \
  --set image.tag=2.0.0
```

## 🧹 Uninstalling

```bash
# Uninstall release
helm uninstall classic-models-api -n classic-models

# Delete namespace (optional)
kubectl delete namespace classic-models
```

## 💡 Tips

1. **Always use `--set-file`** for the SQL initialization script - it's the cleanest method
2. **Use the helper script** for quick installations - it handles everything automatically
3. **Keep secrets secure** - never commit actual passwords to version control
4. **Use values files** for environment-specific configurations
5. **Test with `--dry-run`** before actual deployment

## 🆘 Troubleshooting

If you encounter issues:

```bash
# Check chart syntax
helm lint ./helm/classic-models-api

# Dry run to see generated manifests
helm install classic-models-api ./helm/classic-models-api \
  --dry-run --debug \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql

# Check release status
helm status classic-models-api -n classic-models

# View release history
helm history classic-models-api -n classic-models
```

For more troubleshooting help, see [HELM_DEPLOYMENT.md](../HELM_DEPLOYMENT.md#troubleshooting).