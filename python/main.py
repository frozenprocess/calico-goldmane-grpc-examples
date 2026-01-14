import time
import os
import sys
import json
from google.protobuf.json_format import MessageToJson

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'grpc_libs')))

import grpc
import grpc_libs.api_pb2 as api_pb2
import grpc_libs.api_pb2_grpc as api_pb2_grpc

def get_connection_details():
    """Retrieves connection info from args or defaults."""
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    return "172.18.0.5", "7443"

# --- Configuration ---
target_ip, target_port = get_connection_details()
JSON_FILE = "goldmane_flows.json"
DUMP_INTERVAL_SEC = 1 * 60  # 1 minute

def save_to_json(data_buffer):
    if not data_buffer:
        return
    
    try:
        with open(JSON_FILE, "a") as f:
            # for entry in data_buffer:
                # 1. Convert Protobuf to a Python Dictionary
                # 2. Use json.dumps to ensure strict formatting
                data = json.loads(MessageToJson(data_buffer, preserving_proto_field_name=True))
                if 'flow' in data:
                    json_dict = data['flow']['Key']
                else:
                    json_dict = data
                f.write(json.dumps(json_dict) + "\n")
                
        # print(f"[{time.strftime('%H:%M:%S')}] Saved {len(data_buffer)} valid JSON objects.")
    except Exception as e:
        print(f"File Write Error: {e}")

# Load Certificates
try:
    ca = open("certs/goldmane-ca.crt", "rb").read()
    cert = open("certs/goldmane.crt", "rb").read()
    key = open("certs/goldmane.key", "rb").read()
except FileNotFoundError as e:
    print(f"Error: Certificate file not found: {e}")
    sys.exit(1)

# Establish Secure Channel
# Note: Use 'ca' as the root of trust
creds = grpc.ssl_channel_credentials(ca, key, cert)

# Note: These two lines are a workaround because Goldmane CN excludes the 
# external Service LoadBalancer IP.
target_address = f"ipv4:{target_ip}:{target_port}"
options = (('grpc.ssl_target_name_override', 'goldmane.calico-system.svc'),)
channel = grpc.secure_channel(target_address, creds, options=options)

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
    # page_number=5
)

try:
    stub = api_pb2_grpc.FlowsStub(channel)

    # Customize the request as needed — this is an empty one
    request = api_pb2.FlowListRequest()

    # Call List(), which returns a stream
    for result in stub.List(request):
        print(result)

except Exception as e:
    print(f"gRPC failed with: {e}")


# Optional: you can also build filters just like with List()
# e.g., only flows from `kube-system`
filter_req = api_pb2.Filter(
    # source_namespaces=[
    #     api_pb2.StringMatch(value="kube-system", type=api_pb2.MatchType.Exact)
    # ]
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
    print("Streaming new flows (Ctrl+C to stop)")
    print("Flows are being recorded in %s:"%JSON_FILE)
    for result in stub.Stream(request):
        save_to_json(result)
        # print(result)
except grpc.RpcError as e:
    print(f"gRPC: {e}")
except KeyboardInterrupt:
    save_to_json(result)
    print("\nStream stopped by user.")