#!/bin/bash
set -e

# Classic Models API - Helm Installation Helper Script
# This script simplifies Helm installation with the MySQL initialization script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
RELEASE_NAME="${RELEASE_NAME:-classic-models-api}"
NAMESPACE="${NAMESPACE:-classic-models}"
CHART_PATH="./helm/classic-models-api"
SQL_FILE="./db/mysqlsampledatabase.sql"
VALUES_FILE=""
CREATE_NAMESPACE="true"

# Function to display usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Install Classic Models API using Helm with MySQL initialization script.

OPTIONS:
    -r, --release NAME          Release name (default: classic-models-api)
    -n, --namespace NAMESPACE   Kubernetes namespace (default: classic-models)
    -f, --values FILE           Additional values file
    -s, --sql-file FILE         SQL initialization file (default: ./db/mysqlsampledatabase.sql)
    --no-create-namespace       Don't create namespace if it doesn't exist
    --dry-run                   Perform a dry run
    --debug                     Enable debug output
    -h, --help                  Display this help message

EXAMPLES:
    # Basic installation
    $0

    # Install with custom values
    $0 -f my-values.yaml

    # Install in different namespace
    $0 -n production

    # Install with custom SQL file
    $0 -s /path/to/custom-init.sql

    # Production installation
    $0 -n production -f helm/classic-models-api/values-production.yaml

    # Dry run to see what would be installed
    $0 --dry-run --debug

ENVIRONMENT VARIABLES:
    RELEASE_NAME    Override default release name
    NAMESPACE       Override default namespace

EOF
    exit 1
}

# Parse command line arguments
DRY_RUN=""
DEBUG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--release)
            RELEASE_NAME="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -f|--values)
            VALUES_FILE="$2"
            shift 2
            ;;
        -s|--sql-file)
            SQL_FILE="$2"
            shift 2
            ;;
        --no-create-namespace)
            CREATE_NAMESPACE="false"
            shift
            ;;
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Classic Models API - Helm Installation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    echo "Please install Helm from: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo -e "${GREEN}✓ Helm found: $(helm version --short)${NC}"

# Check if kubectl/oc is installed
if command -v oc &> /dev/null; then
    CLI="oc"
    echo -e "${GREEN}✓ OpenShift CLI found${NC}"
elif command -v kubectl &> /dev/null; then
    CLI="kubectl"
    echo -e "${GREEN}✓ Kubernetes CLI found${NC}"
else
    echo -e "${RED}Error: Neither kubectl nor oc CLI found${NC}"
    exit 1
fi

# Check if chart exists
if [ ! -d "$CHART_PATH" ]; then
    echo -e "${RED}Error: Chart not found at $CHART_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Chart found at $CHART_PATH${NC}"

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}Error: SQL file not found at $SQL_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ SQL file found at $SQL_FILE${NC}"
echo ""

# Add Bitnami repository
echo -e "${YELLOW}Adding Bitnami Helm repository...${NC}"
helm repo add bitnami https://charts.bitnami.com/bitnami 2>/dev/null || true
helm repo update
echo -e "${GREEN}✓ Bitnami repository updated${NC}"
echo ""

# Build helm command
HELM_CMD="helm install $RELEASE_NAME $CHART_PATH"
HELM_CMD="$HELM_CMD --namespace $NAMESPACE"

if [ "$CREATE_NAMESPACE" = "true" ]; then
    HELM_CMD="$HELM_CMD --create-namespace"
fi

# Add SQL file using --set-file
HELM_CMD="$HELM_CMD --set-file mysql.initdbScripts.01-init\\.sql=$SQL_FILE"

# Add custom values file if provided
if [ -n "$VALUES_FILE" ]; then
    if [ ! -f "$VALUES_FILE" ]; then
        echo -e "${RED}Error: Values file not found at $VALUES_FILE${NC}"
        exit 1
    fi
    HELM_CMD="$HELM_CMD -f $VALUES_FILE"
    echo -e "${GREEN}✓ Using values file: $VALUES_FILE${NC}"
fi

# Add dry-run and debug flags
if [ -n "$DRY_RUN" ]; then
    HELM_CMD="$HELM_CMD $DRY_RUN"
    echo -e "${YELLOW}Running in dry-run mode${NC}"
fi

if [ -n "$DEBUG" ]; then
    HELM_CMD="$HELM_CMD $DEBUG"
fi

echo ""
echo -e "${YELLOW}Installation Details:${NC}"
echo "  Release Name: $RELEASE_NAME"
echo "  Namespace: $NAMESPACE"
echo "  Chart: $CHART_PATH"
echo "  SQL File: $SQL_FILE"
[ -n "$VALUES_FILE" ] && echo "  Values File: $VALUES_FILE"
echo ""

# Confirm installation (skip in dry-run mode)
if [ -z "$DRY_RUN" ]; then
    read -p "Proceed with installation? (yes/no): " -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Execute helm install
echo -e "${YELLOW}Installing Helm chart...${NC}"
echo ""
echo -e "${BLUE}Command: $HELM_CMD${NC}"
echo ""

eval $HELM_CMD

if [ $? -eq 0 ]; then
    if [ -z "$DRY_RUN" ]; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Installation Complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "To check the status:"
        echo "  helm status $RELEASE_NAME -n $NAMESPACE"
        echo ""
        echo "To view pods:"
        echo "  $CLI get pods -n $NAMESPACE"
        echo ""
        echo "To view logs:"
        echo "  $CLI logs -f deployment/$RELEASE_NAME -n $NAMESPACE"
        echo ""
        
        # Get route/ingress URL
        if [ "$CLI" = "oc" ]; then
            echo "To get the Route URL:"
            echo "  oc get route $RELEASE_NAME -n $NAMESPACE -o jsonpath='{.spec.host}'"
        else
            echo "To get the Ingress URL:"
            echo "  kubectl get ingress $RELEASE_NAME -n $NAMESPACE"
        fi
        echo ""
    fi
else
    echo -e "${RED}Installation failed!${NC}"
    exit 1
fi

# Made with Bob
