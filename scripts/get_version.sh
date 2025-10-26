#!/bin/bash
# Get current version from git tag and export as API_VERSION

# Get the latest git tag
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

if [ -n "$CURRENT_TAG" ]; then
    # Remove 'v' prefix if present
    VERSION=${CURRENT_TAG#v}
    echo "Current git tag: $CURRENT_TAG"
    echo "Setting API_VERSION to: $VERSION"
    export API_VERSION=$VERSION
else
    echo "No git tag found, using default version 1.0.0"
    export API_VERSION=1.0.0
fi

echo "API_VERSION is set to: $API_VERSION"
