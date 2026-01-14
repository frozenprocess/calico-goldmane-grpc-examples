# Installing Goldmane
This tutorial uses bash and grpcurl to communicate with Goldmane.

# Requirements

- Kubernetes
- An operator based Calico installation v3.30 or higher

# gRPC 101
To use gRPC services you need to know what services are supported by the server. There are two ways to find out what a server offers:

* gRPC reflection
* gRPC proto file
Currently Goldmane uses a protobuf file, and this file can be found in the Calico repository. Since gRPC implements its own standard we need a client that can communicate and understand gRPC. For this post we are going to use gRPCurl a simple command line utility that can be used to communicate with any gRPC server.

# Deploying gRPCurl
Network flows are sensitive information and that is why we have taken security measures such as mTLS and default network security policies to make sure this information is only accessible to authorized users. Now, if someone has access to the right certificates and is permitted by network security policies to access goldmane they can use the ClusterIP service that is created by Tigera operator to access Goldmane inside the cluster.

Use the following command to create a gRPCurl deployment in your cluster:

```bash
kubectl create -f https://raw.githubusercontent.com/frozenprocess/calico-goldmane-grpc-examples/refs/heads/main/grpcurl/grpcurl.yaml
```

After gRPCurl deployment is complete we can access it using kubectl.
Use the following command to access the gRPCurl deployment pod:

```bash
kubectl exec -it -n calico-system deployment/grpcurl -- /bin/sh
```

Use the following command to download the api.proto file:
```bash
wget https://raw.githubusercontent.com/projectcalico/calico/refs/heads/master/goldmane/proto/api.proto
```

After downloading the `api.proto` file from the Calico repository we can use the `gRPCurl` to list the services that Goldmane offers.

Use the following command to see the services that Goldmane offers:

```bash
grpcurl -proto api.proto goldmane.calico-system.svc:7443 list
```

## Goldmane Services
At the time of writing this article, Goldmane implements three services:

* FlowCollector: used by Calico Felix (or any other program) to publish network flow information to Goldmane.
* Flows: which can be used by our client to get the network flows cached in Goldmane memory.
* Statistics: Which offers a detailed tally about your cluster policies with information such as packet allowed or denied.

Each of these services have functions that can be invoked, but the main ones of interest will be the Flows and Statistics APIs (unless you’re modifying Felix itself!).

For example, let’s go ahead and check what functions are available within the Flows services.

Use the following command to check the functions available:

```bash
grpcurl -proto api.proto goldmane.calico-system.svc:7443 describe goldmane.Flows
```

You should see a result similar to the following:

```bash
service Flows {
  // FilterHints can be used to discover available filter criteria, such as
  // Namespaces and source / destination names. It allows progressive filtering of criteria based on
  // other filters. i.e., return the flow destinations given a source namespace.
  // Note that this API provides hints to the UI based on past flows and other values may be valid.
  rpc FilterHints ( .goldmane.FilterHintsRequest ) returns ( .goldmane.FilterHintsResult );
  // List is an API call to query for one or more Flows.
  rpc List ( .goldmane.FlowListRequest ) returns ( .goldmane.FlowListResult );
  // Stream is an API call to return a long running stream of new Flows as they are generated.
  rpc Stream ( .goldmane.FlowStreamRequest ) returns ( stream .goldmane.FlowResult );
}
```

Now let’s query one of the “List” function and see what happens
```bash
grpcurl -proto api.proto goldmane.calico-system.svc:7443 goldmane.Flows/List
```

You should see an error similar to the following:

```bash
Failed to dial target host "goldmane.calico-system.svc:7443": tls: failed to verify certificate: x509: certificate signed by unknown authority
```

## It’s usually a certificate issue

You might be wondering why I got this error? If you recall earlier we talked about Goldmane expecting mTLS from its client, and this error message verifies that our service is in fact expecting a certificate as a form of authentication.

To fix this issue we can use the certificates that are mounted in this deployment.

Use the following command to scrape the information:
```bash
grpcurl -proto api.proto -cacert /etc/goldmane/certs/tls.crt -cert /etc/goldmane/certs/tls.crt -key /etc/goldmane/certs/tls.key goldmane.calico-system.svc:7443 goldmane.Flows/List
```
