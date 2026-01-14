# Tutorial: Connecting to Goldmane with Python gRPC

## Requirements

This tutorial assumes you have a running Kubernetes cluster equipped with Calico and a basic knowledge of Python.
Prerequisites:
* Python
* Kubernetes
* Calico v3.30 or higher

1. Environment Setup
First, install the necessary dependencies and create the directory structure for your certificates and gRPC libraries.
```bash
pip install requirements
mkdir certs grpc_libs
```

Download the proto model for the version of Calico that you are running.
```bash
curl -L https://raw.githubusercontent.com/projectcalico/calico/refs/heads/master/goldmane/proto/api.proto -o grpc_libs/api.proto
```

Use the `grpc_tools` to build the necessary grpc libraries.
```bash
python -m grpc_tools.protoc --proto_path=./grpc_libs --python_out=grpc_libs/. --pyi_out=grpc_libs/. --grpc_python_out=grpc_libs/. grpc_libs/api.proto
```

## Extract Goldmane Certificates
Goldmane publishes an identity-based endpoint. Clients can only communicate with Goldmane if they possess an identity verified by the Goldmane CA.

In this section, you will extract the existing Goldmane certificates from the cluster.

> **Warning:** Extracting the internal CA keys is not recommended for production environments. In a production scenario, you should use your own Certificate Authority (CA) to issue a unique identity for the Goldmane client you are building.

Export the Goldmane CA bundle:
```bash
kubectl get cm -n calico-system goldmane-ca-bundle -o jsonpath="{.data.tigera-ca-bundle\.crt}" > certs/goldmane-ca.crt
```

Use the following command to export the Goldmane certificate:
```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.crt}" | base64 -d > certs/goldmane.crt
```

Use the following command to export the Goldmane private keys:
```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.key}" | base64 -d > certs/goldmane.key
```

## Expose the Goldmane Service

To allow your local Python client to reach the service inside the cluster, create a `LoadBalancer` type service.
```bash
kubectl create -f svc.yaml
```

Verify the service is running and retrieve the external IP address:
```bash
kubectl get svc -A
```

Example Output:
```bash
NAME                              TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
goldmane-ext                      LoadBalancer   10.96.188.241   172.18.0.5    7443:31356/TCP   4h56m
```

## Verify the Client

Use the IP address from the previous step and connect to Goldmane.
```bash
python main.py 172.18.0.5 7443
```

The system will return the following statements, and after a short perid flows will be captured by the program.
```bash
gRPC failed with: 'FlowListResult' object is not iterable
Streaming new flows (Ctrl+C to stop)
Flows are being recorded in goldmane_flows.json:
```
