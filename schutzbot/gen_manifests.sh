#!/bin/bash
set -euxo pipefail

git clone https://github.com/osbuild/osbuild-composer.git
cd osbuild-composer
echo "Installing build dependencies"
sudo dnf install -y redhat-rpm-config
sudo dnf config-manager --set-enabled codeready-builder-for-rhel-9-rhui-rpms
sudo dnf build-dep -y osbuild-composer.spec
echo "Generating manifests"
go run ./cmd/gen-manifests -workers 50 -output ../manifests

if [ "${COMPOSER_REMOTE:-}" ]; then
    cd ..
    mv manifests tmp
    mkdir manifests
    git clone ${COMPOSER_REMOTE} osbuild-composer2
    cd osbuild-composer2
    git checkout ${COMPOSER_BRANCH}
    echo "Installing build dependencies"
    sudo dnf build-dep -y osbuild-composer.spec
    echo "Generating manifests"
    go run ./cmd/gen-manifests -workers 50 -output ../manifests2
    cd ..
    echo "Keeping only the different ones"
    cd manifests2
    for f in *
    do
         diff ${f} ../tmp/${f} || mv ${f} ../manifests/${f}
    done
fi
