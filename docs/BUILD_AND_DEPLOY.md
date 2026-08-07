# Building and Deploying to Your Own GitHub Repository

This guide explains how to build Docker images and deploy the Classic Models API from your own GitHub repository.

## Prerequisites

- GitHub account
- Git installed locally
- Docker installed (for local testing)
- Access to a Kubernetes/OpenShift cluster (for deployment)

## Step 1: Fork or Clone the Repository

### Option A: Fork the Repository (Recommended)
1. Go to the original repository on GitHub
2. Click the "Fork" button in the top right
3. Clone your forked repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/classic-models-api.git
   cd classic-models-api
   ```

### Option B: Create a New Repository
1. Create a new repository on GitHub (e.g., `classic-models-api`)
2. Clone this repository locally
3. Add your new GitHub repository as the remote:
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/classic-models-api.git
   git push -u origin main
   ```

## Step 2: Enable GitHub Container Registry

The workflow is already configured to use GitHub Container Registry (ghcr.io). No additional setup is required - the `GITHUB_TOKEN` is automatically available in GitHub Actions.

### Verify Permissions
1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Scroll to **Workflow permissions**
4. Ensure **Read and write permissions** is selected
5. Check **Allow GitHub Actions to create and approve pull requests**

## Step 3: Build Docker Images

The GitHub Actions workflow (`.github/workflows/docker-build.yml`) automatically builds and pushes Docker images when you create a version tag.

### Automatic Build on Tag Push

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This will:
- Build Docker images for `linux/amd64` and `linux/arm64`
- Push to `ghcr.io/YOUR_USERNAME/classic-models-api:v1.0.0`
- Tag as `latest` if this is the highest version
- Create a GitHub Release with deployment instructions

### Manual Build Trigger

You can also trigger the build manually:
1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Build and Push Docker Image** workflow
4. Click **Run workflow**
5. Select the branch and click **Run workflow**

## Step 4: Make Your Image Public (Optional)

By default, GitHub Container Registry images are private. To make them public:

1. Go to https://github.com/YOUR_USERNAME?tab=packages
2. Find your `classic-models-api` package
3. Click on the package
4. Click **Package settings** (right sidebar)
5. Scroll to **Danger Zone**
6. Click **Change visibility** → **Public**

## Step 5: Update Helm Chart to Use Your Image

Update the Helm values to use your Docker image:

```bash
# Create a custom values file
cat > my-values.yaml <<EOF
image:
  repository: ghcr.io/YOUR_USERNAME/classic-models-api
  tag: v1.0.0
  pullPolicy: IfNotPresent

# If your image is private, add imagePullSecrets
imagePullSecrets:
  - name: ghcr-secret
EOF
```

### Create Image Pull Secret (for private images)

If your image is private, create a secret:

```bash
# Create a GitHub Personal Access Token with read:packages scope
# Then create the secret:
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  -n classic-models
```

## Step 6: Deploy with Helm

```bash
# Deploy using your custom image
helm install classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  -f helm/classic-models-api/values-openshift.yaml \
  --set mysql.enabled=false \
  --set mysql.externalHost=YOUR_MYSQL_HOST \
  --set mysql.auth.password=YOUR_MYSQL_PASSWORD \
  --namespace classic-models \
  --create-namespace
```

## Step 7: Verify Deployment

```bash
# Check if pods are running
kubectl get pods -n classic-models

# Check the image being used
kubectl describe pod -n classic-models -l app.kubernetes.io/name=classic-models-api | grep Image:

# Check logs
kubectl logs -n classic-models -l app.kubernetes.io/name=classic-models-api
```

## Local Development and Testing

### Build Locally

```bash
# Build for your platform
docker build -t classic-models-api:local .

# Test locally
docker run -p 8000:8000 \
  -e DEBUG=1 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_DATABASE=classicmodels \
  -e MYSQL_USER=classicuser \
  -e MYSQL_PASSWORD=classicpass \
  classic-models-api:local
```

### Push to Your Registry Manually

```bash
# Tag the image
docker tag classic-models-api:local ghcr.io/YOUR_USERNAME/classic-models-api:v1.0.0

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Push the image
docker push ghcr.io/YOUR_USERNAME/classic-models-api:v1.0.0
```

## Version Management

### Semantic Versioning

Use semantic versioning for releases:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)

### Creating Releases

```bash
# Create a new version
git tag v1.1.0
git push origin v1.1.0

# The GitHub Action will:
# 1. Build and push the Docker image
# 2. Tag as 'latest' if this is the highest version
# 3. Create a GitHub Release with deployment instructions
```

## Troubleshooting

### Build Fails

Check the GitHub Actions logs:
1. Go to **Actions** tab
2. Click on the failed workflow run
3. Review the logs for errors

Common issues:
- **Permission denied**: Check workflow permissions in repository settings
- **Image push failed**: Verify GITHUB_TOKEN has packages:write permission
- **Build timeout**: Large images may need more time; consider optimizing Dockerfile

### Image Pull Errors

If pods can't pull the image:
```bash
# Check image pull secrets
kubectl get secrets -n classic-models

# Describe the pod to see the error
kubectl describe pod POD_NAME -n classic-models

# Verify the image exists
docker pull ghcr.io/YOUR_USERNAME/classic-models-api:v1.0.0
```

### Update Existing Deployment

```bash
# Update to a new version
helm upgrade classic-models-api ./helm/classic-models-api \
  -f my-values.yaml \
  --set image.tag=v1.1.0 \
  -n classic-models

# Rollback if needed
helm rollback classic-models-api -n classic-models
```

## CI/CD Best Practices

1. **Use version tags**: Always tag releases with semantic versions
2. **Test before tagging**: Run tests locally before pushing tags
3. **Review releases**: Check the GitHub Release notes after each build
4. **Monitor deployments**: Watch pod status after deploying new versions
5. **Keep secrets secure**: Never commit secrets to the repository
6. **Use staging**: Test new versions in a staging environment first

## Additional Resources

- [GitHub Container Registry Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)