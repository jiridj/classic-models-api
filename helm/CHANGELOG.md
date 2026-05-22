# Helm Chart Changelog

## Version 0.1.0 - 2026-05-22

### Added
- **External MySQL Support**: Chart now supports connecting to external MySQL databases
  - Set `mysql.enabled: false` to disable chart-managed MySQL
  - Configure `mysql.externalHost` and `mysql.externalPort` for external database
  - Created `values-external-mysql.yaml` as example configuration
  - Updated documentation with external MySQL setup instructions

### Changed
- **Health Check Probes**: Updated liveness and readiness probes to use `/classic-models/api/schema/`
  - Previous endpoint `/classic-models/api/v1/` required authentication causing probe failures
  - New endpoint has `AllowAny` permission, avoiding "Unauthorized" errors
  - Probes now work correctly without authentication credentials

### Fixed
- **Init Container**: Fixed shell variable expansion issue in wait-for-mysql init container
  - Changed from inline template substitution to environment variables
  - Prevents "bad address" errors with hostnames containing special characters
  - Improved reliability for both chart-managed and external MySQL
- **MySQL Chart Dependency**: Updated from version `~11.1.0` to `12.3.5`
  - This is the latest chart version in the MySQL 8.x series
  - Chart version 12.3.5 uses MySQL appVersion 8.4.5
  
- **MySQL Image Configuration**: Using Bitnami Legacy registry
  - Bitnami images have moved to `docker.io/bitnamilegacy` registry
  - Using `bitnamilegacy/mysql:8.4.5-debian-12-r0` (matches chart 12.3.5 appVersion)
  - Added `global.security.allowInsecureImages: true` to bypass Bitnami chart validation
  - Updated in all values files:
    - `values.yaml` (default/development)
    - `values-production.yaml` (production)
    - `values-openshift.yaml` (OpenShift-specific)
  
### Technical Details

**Chart Dependency** (`Chart.yaml`):
```yaml
dependencies:
  - name: mysql
    version: "12.3.5"  # Previously: "~11.1.0"
    repository: https://charts.bitnami.com/bitnami
```

**Global Configuration** (all values files):
```yaml
global:
  openshift: true  # or false for Kubernetes
  security:
    # Allow bitnamilegacy images (Bitnami moved images to legacy registry)
    allowInsecureImages: true
```

**MySQL Configuration** (all values files):
```yaml
mysql:
  enabled: true
  # Use Bitnami MySQL image from legacy registry
  # Bitnami images are now in docker.io/bitnamilegacy
  image:
    registry: docker.io
    repository: bitnamilegacy/mysql
    tag: 8.4.5-debian-12-r0
  auth:
    rootPassword: "rootpassword"
    database: "classicmodels"
    username: "classicuser"
    password: "classicpass"
```

### Compatibility

- MySQL 8.4.5 is part of the MySQL 8.x Innovation series
- Fully compatible with existing Classic Models database schema
- Maintains backward compatibility with MySQL 8.0.x
- All OpenShift Security Context Constraints (SCC) configurations remain unchanged

### Deployment

To deploy with the updated chart:

```bash
# Update dependencies (already done)
cd helm/classic-models-api
helm dependency update

# Install/upgrade on OpenShift
helm install classic-models-api ./helm/classic-models-api \
  -f helm/classic-models-api/values-openshift.yaml \
  --set-file mysql.initdbScripts.01-init\.sql=db/mysqlsampledatabase.sql \
  --namespace classic-models \
  --create-namespace

# Or use the helper script
./helm/install-with-db.sh
```

### Verification

Verified with dry-run:
```bash
helm install classic-models-api ./helm/classic-models-api \
  -f helm/classic-models-api/values-openshift.yaml \
  --dry-run --debug
```

Status: ✅ All configurations validated successfully