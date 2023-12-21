#!/bin/bash
set -euxo pipefail

git clone https://github.com/osbuild/images.git
cd images
echo "Installing build dependencies"
sudo dnf install -y redhat-rpm-config
sudo dnf config-manager --set-enabled codeready-builder-for-rhel-9-rhui-rpms
sudo dnf build-dep -y osbuild-composer
echo "Generating manifests"
go run ./cmd/gen-manifests -workers 50 -output ../manifests
