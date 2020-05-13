#!/bin/bash

# Install build requirements
dnf install -y gcc python3-devel openssl-devel python3-pip
dnf clean all
