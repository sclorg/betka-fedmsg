#!/bin/bash

# Install build requirements
dnf install -y gcc python3-devel openssl-devel
dnf clean all
