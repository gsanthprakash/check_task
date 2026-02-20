#!/bin/bash
set -e

echo "Restoring correct UI ingress configuration..."

kubectl patch ingress ui-ingress -n app \
  --type=merge \
  -p '{
    "spec": {
      "rules": [
        {
          "host": "ui.devops.local",
          "http": {
            "paths": [
              {
                "path": "/",
                "pathType": "Prefix",
                "backend": {
                  "service": {
                    "name": "ui-service",
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

echo "Ingress configuration restored."
echo "Expected state: UI and static assets accessible, API unaffected."
