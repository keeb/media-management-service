#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "==> Assembling build context in $BUILD_DIR"

# Copy binaries
cp "$REPO_ROOT/dist/mms" "$BUILD_DIR/mms"
cp /home/keeb/git/swamp/swamp "$BUILD_DIR/swamp"

# Copy .swamp.yaml
cp "$REPO_ROOT/.swamp.yaml" "$BUILD_DIR/.swamp.yaml"

# Copy Dockerfile
cp "$SCRIPT_DIR/Dockerfile" "$BUILD_DIR/Dockerfile"

# Assemble minimal .swamp/ directory
mkdir -p "$BUILD_DIR/.swamp/definitions/command/shell"
mkdir -p "$BUILD_DIR/.swamp/workflows"
mkdir -p "$BUILD_DIR/.swamp/vault/local_encryption"
mkdir -p "$BUILD_DIR/.swamp/secrets/local_encryption/homelab"

# Copy and patch the inventory-scan model definition
sed \
  -e 's|workingDir: /home/keeb/git/media-management-service|workingDir: /opt/mms|' \
  -e 's|run: ./dist/mms|run: ./mms|' \
  "$REPO_ROOT/.swamp/definitions/command/shell/f6532e0c-3d3e-45c8-a602-70fc20e83652.yaml" \
  > "$BUILD_DIR/.swamp/definitions/command/shell/f6532e0c-3d3e-45c8-a602-70fc20e83652.yaml"

# Copy the media-inventory workflow as-is
cp "$REPO_ROOT/.swamp/workflows/workflow-4d54262a-a48e-45cd-87fc-ee408eac649f.yaml" \
   "$BUILD_DIR/.swamp/workflows/"

# Copy and patch the vault definition
sed \
  -e 's|base_dir: /home/keeb/git/media-management-service|base_dir: /opt/mms|' \
  "$REPO_ROOT/.swamp/vault/local_encryption/86aec9ce-6b14-44ba-a630-4a0f673798ed.yaml" \
  > "$BUILD_DIR/.swamp/vault/local_encryption/86aec9ce-6b14-44ba-a630-4a0f673798ed.yaml"

# Copy secrets (key + encrypted value)
cp "$REPO_ROOT/.swamp/secrets/local_encryption/homelab/.key" \
   "$BUILD_DIR/.swamp/secrets/local_encryption/homelab/.key"
cp "$REPO_ROOT/.swamp/secrets/local_encryption/homelab/jellyfin-api-key.enc" \
   "$BUILD_DIR/.swamp/secrets/local_encryption/homelab/jellyfin-api-key.enc"

echo "==> Building Docker image mms-inventory"
docker build -t mms-inventory "$BUILD_DIR"

echo "==> Done. Image: mms-inventory"
