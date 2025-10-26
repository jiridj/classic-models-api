# Release Management Guide

This guide explains how to manage releases for the Classic Models API using semantic versioning and automated CI/CD.

## Overview

The release management system automatically:
- Builds Docker images when you create git tags
- Tags images with both the version and `latest`
- Updates API documentation version
- Creates GitHub releases
- Supports semantic versioning (semver)

## Creating a Release

### 1. Prepare Your Release

Before creating a release, ensure:
- All changes are committed to the `main` branch
- Tests are passing
- Documentation is updated
- Version numbers are appropriate

### 2. Create a Git Tag

Use semantic versioning format: `vMAJOR.MINOR.PATCH`

```bash
# Examples:
git tag v1.0.0    # Major release
git tag v1.1.0    # Minor release (new features)
git tag v1.1.1    # Patch release (bug fixes)

# Push the tag to trigger the release
git push origin v1.0.0
```

### 3. Automated Release Process

When you push a tag, GitHub Actions will automatically:

1. **Extract Version**: Parse the tag (e.g., `v1.0.0` → `1.0.0`)
2. **Update API Version**: Update the version in `config/settings/base.py`
3. **Build Docker Image**: Create multi-architecture image (AMD64/ARM64)
4. **Push to Registry**: Push to GitHub Container Registry with tags:
   - `ghcr.io/your-username/classic-models-api:v1.0.0`
   - `ghcr.io/your-username/classic-models-api:latest`
5. **Create GitHub Release**: Generate release notes and download links

## Version Management

### API Documentation Version

The API documentation version is automatically updated from git tags:

- **Swagger UI**: Shows the current version in the title
- **ReDoc**: Displays version information
- **OpenAPI Schema**: Includes version metadata

### Version Script

A Python script (`scripts/version.py`) manages version updates:

```bash
# Update to a specific version
python scripts/version.py 1.0.0

# Auto-detect version from git
python scripts/version.py
```

## Deployment

### Using Versioned Images

Update your `.env` file to use specific versions:

```bash
# Use latest version
API_VERSION=latest

# Use specific version
API_VERSION=v1.0.0

# Use development version
API_VERSION=dev-abc123
```

### Docker Compose

The Docker Compose file supports versioned deployments:

```yaml
api:
  image: ghcr.io/your-username/classic-models-api:${API_VERSION:-latest}
```

## Release Types

### Major Release (v2.0.0)
- Breaking changes
- New major features
- Significant architectural changes

### Minor Release (v1.1.0)
- New features
- Backward compatible
- API additions

### Patch Release (v1.0.1)
- Bug fixes
- Security updates
- Performance improvements

## Release Checklist

Before creating a release:

- [ ] All features are complete and tested
- [ ] Documentation is updated
- [ ] API version is appropriate
- [ ] Breaking changes are documented
- [ ] Migration guides are provided (if needed)
- [ ] Security vulnerabilities are addressed

## Rollback Strategy

If a release has issues:

1. **Immediate**: Use previous version in `.env`:
   ```bash
   API_VERSION=v1.0.0  # Previous stable version
   ```

2. **Redeploy**: Restart containers with the previous version:
   ```bash
   docker compose down
   docker compose up -d
   ```

3. **Hotfix**: Create a patch release:
   ```bash
   git tag v1.0.2
   git push origin v1.0.2
   ```

## Monitoring Releases

### GitHub Actions

Monitor release builds:
- Go to Actions tab in your repository
- Check for successful builds
- Review any failed builds

### Container Registry

Check published images:
- Visit `https://github.com/your-username/classic-models-api/pkgs/container/classic-models-api`
- Verify tags are created correctly
- Check image sizes and layers

### API Health

After deployment:
- Test API endpoints
- Verify documentation version
- Check authentication
- Monitor logs

## Best Practices

### Semantic Versioning

Follow semver guidelines:
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Release Notes

GitHub releases include:
- Version information
- Docker image tags
- API documentation links
- Deployment instructions

### Testing

Before releasing:
- Run full test suite
- Test Docker image locally
- Verify API documentation
- Check authentication flow

## Troubleshooting

### Failed Builds

If GitHub Actions fails:
1. Check the Actions logs
2. Verify git tag format
3. Ensure all files are committed
4. Check Docker build context

### Version Not Updating

If API version doesn't update:
1. Check `config/settings/base.py`
2. Verify git tag format
3. Run version script manually
4. Check GitHub Actions logs

### Image Not Found

If Docker image isn't available:
1. Check GitHub Container Registry
2. Verify image tags
3. Check permissions
4. Verify repository name

## Examples

### Creating Your First Release

```bash
# 1. Ensure everything is committed
git add .
git commit -m "Prepare for v1.0.0 release"

# 2. Create and push tag
git tag v1.0.0
git push origin v1.0.0

# 3. Monitor GitHub Actions
# 4. Check GitHub Container Registry
# 5. Update deployment
```

### Updating Deployment

```bash
# Update .env file
echo "API_VERSION=v1.0.0" >> .env

# Restart services
docker compose down
docker compose up -d

# Verify deployment
curl http://your-nas-ip:8000/api/docs/
```

This release management system ensures consistent, automated releases with proper versioning and documentation updates.
