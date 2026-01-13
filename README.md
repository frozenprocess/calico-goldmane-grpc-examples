To the 2025 Kubecon and beyond
===
This repository provides examples and tools for interacting with **Calico Goldmane**, the gRPC-based flow logs and observability API introduced in Calico v3.30. Goldmane is the backend engine that powers the Calico Whisker console, providing real-time insights into network traffic and policy enforcement.

## Project Structure

- **/grpcurl**: Contains manifests to deploy a `grpcurl` pod pre-configured with the necessary volume mounts to access Goldmane's mTLS certificates.
- **/python**: A Python-based gRPC client example showing how to programmatically connect to Goldmane, list flows, and listen to the flow stream.

## Features

- **Flow Analysis**: Query real-time flow data with workload-specific context.
- **Policy Statistics**: See exactly which policies and rules are allowing or denying traffic.
- **Secure by Default**: Examples demonstrate how to handle mTLS authentication required by Goldmane.


# Security Note

Goldmane handles sensitive network metadata. Because of this, it requires Mutual TLS (mTLS) for all connections. Ensure your clients have access to the goldmane-key-pair secret created by the Tigera operator.

# Resources

CalicoCon Live session [YouTube](https://www.youtube.com/watch?v=nmOjnbmihJA)
