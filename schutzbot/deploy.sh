#!/bin/bash
set -euxo pipefail


# set locale to en_US.UTF-8
sudo dnf install -y glibc-langpack-en git make
sudo dnf -y install skopeo \
        make \
        git \
        go \
        openssl \
        rpm-build \
        setools-console \
        setroubleshoot \
        container-selinux \
        lvm2
localectl set-locale LANG=en_US.UTF-8

# Colorful output.
function greenprint {
    echo -e "\033[1;32m[$(date -Isecond)] ${1}\033[0m"
}

# clone the latest osbuild

git clone https://github.com/osbuild/osbuild.git

# install the latest osbuild

cd osbuild
sudo dnf -q builddep -y osbuild.spec
make rpm
sudo dnf install ./rpmbuild/RPMS/noarch/*.rpm  -y


greenprint "OSBuild installed"
