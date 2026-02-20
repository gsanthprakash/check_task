#!/bin/bash
set -e

echo "Setting up broken environment..."

# Apply base Kubernetes manifests
kubectl apply -f k8s/

echo "Introducing configuration drift..."

# BREAK-1: Ingress routes UI traffic to a non-existent service
kubectl patch ingress ui-ingress -n app \
  --type=merge \
  -p '{
    "spec": {
      "rules": [
        {
          "http": {
            "paths": [
              {
                "path": "/",
                "pathType": "Prefix",
                "backend": {
                  "service": {
                    "name": "wrong-service",
                    "port": {
                      "number": 80
                    }
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }'

echo "Ingress misconfiguration applied."

# BREAK-2: Make MinIO UI assets bucket private
echo "Restricting access to MinIO UI assets..."

mc alias set local http://minio:9000 minioadmin minioadmin
mc anonymous set none local/ui-assets

echo "MinIO bucket access restricted."

echo "Environment setup complete."
echo "Expected state: API healthy, UI and static assets failing."