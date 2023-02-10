#!/bin/bash

git remote add ghorigin https://github.com/osbuild/manifest-db.git
git fetch ghorigin

if $(git diff --name-only origin/main | grep tools/image-info); then
    set -euxo pipefail
    schutzbot/deploy.sh
    schutzbot/selinux-context.sh
    tests/cases/manifest_tests
else
    echo "no need to test image-info"
fi
