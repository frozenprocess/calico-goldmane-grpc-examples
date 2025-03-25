import grpc
import api_pb2
import api_pb2_grpc
import time

ca = open("certs/operator.crt","rb").read()
cert = open("certs/goldmane.crt","rb").read()
key = open("certs/goldmane.key","rb").read()

creds = grpc.ssl_channel_credentials(cert,key,cert)
# channel = grpc.secure_channel("goldmane.calico-system.svc:7443", creds)
channel = grpc.secure_channel("goldmane:7443", creds)


# Time range: last 15 minutes in nanoseconds
now_ns = int(time.time() * 1e9)
fifteen_min_ago_ns = now_ns - 15 * 60 * int(1e9)

# Build a namespace filter: from any source to destination in "kube-system"
namespace_match = api_pb2.StringMatch(
    value="kube-system",
    type=api_pb2.MatchType.Exact
)

# Construct the full filter
flow_filter = api_pb2.Filter(
    dest_namespaces=[namespace_match]
)

# Add sorting by time
sort_option = api_pb2.SortOption(sort_by=api_pb2.SortBy.Time)

# FlowListRequest message
request = api_pb2.FlowListRequest(
    start_time_gte=fifteen_min_ago_ns,
    start_time_lt=now_ns,
    filter=flow_filter,
    sort_by=[sort_option],
    page_size=50,
    page_number=5
)

try:
    stub = api_pb2_grpc.FlowsStub(channel)

    # Customize the request as needed — this is an empty one
    request = api_pb2.FlowListRequest()

    # Call List(), which returns a stream
    for result in stub.List(request):
        print(result)

except Exception as e:
    print(f"gRPC failed with code: {e.code()}, message: {e.details()}")


# Optional: you can also build filters just like with List()
# e.g., only flows from `kube-system`
filter_req = api_pb2.Filter(
    source_namespaces=[
        api_pb2.StringMatch(value="kube-system", type=api_pb2.MatchType.Exact)
    ]
)

# Build Stream request
request = api_pb2.FlowStreamRequest(
    start_time_gte=now_ns,  # Only new flows from now onward
    filter=filter_req,
    aggregation_interval=0  # Optional, set if you want aggregation
)

request = api_pb2.FlowStreamRequest(
    start_time_gte=now_ns,  # Only new flows from now onward
    filter=filter_req,
    aggregation_interval=15  # Optional, set if you want aggregation
)


try:
    print("Streaming new flows (Ctrl+C to stop):\n")
    for result in stub.Stream(request):
        print(result)
except grpc.RpcError as e:
    print(f"gRPC error: {e.code()} - {e.details()}")
except KeyboardInterrupt:
    print("\nStream stopped by user.")