# TSAR Kubernetes example

This is a **local demonstration**, not a production deployment. The sample application is built from the adjacent Dockerfile and serves HTTPS health endpoints on port 8443.

## Local run with kind

1. Create the namespace:

```bash
kubectl apply -f namespace.yaml
```

2. Generate a local self-signed certificate and create the TLS Secret. Do not commit the private key:

```bash
openssl req -x509 -nodes -newkey rsa:3072 -keyout tls.key -out tls.crt -days 365 -subj "/CN=tsar-app.tsar-example.svc"
kubectl -n tsar-example create secret tls tsar-app-tls --cert=tls.crt --key=tls.key
```

3. Build and load the example image into your kind cluster:

```bash
docker build -t tsar-example-app:local app/
kind load docker-image tsar-example-app:local --name <kind-cluster-name>
```

4. Apply the local runtime resources:

```bash
kubectl apply -f configmap.yaml
kubectl apply -f serviceaccount.yaml
kubectl apply -f service.yaml
kubectl apply -f networkpolicy.yaml
kubectl apply -f poddisruptionbudget.yaml
kubectl apply -f deployment.yaml
kubectl -n tsar-example rollout status deployment/tsar-app
```

The \`imagePullPolicy: Never\` setting is intentional for this local kind example. For a remote cluster, build and publish the image to a trusted registry, scan and sign it, then replace the image reference with the published immutable digest and use \`IfNotPresent\`.

## Optional External Secrets example

\`secret.yaml\` is an \`ExternalSecret\` custom resource. Apply it only after installing a compatible External Secrets Operator and creating the referenced \`ClusterSecretStore\` named \`aws-secrets-manager\`. The AWS identity, IAM permissions, and remote secret names must be configured in the target environment. This optional resource is not required by the minimal health application.

The example intentionally does not contain a TLS private key, application credentials, AWS account ID, or registry digest.
