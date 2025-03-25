```bash
curl -L https://raw.githubusercontent.com/projectcalico/calico/refs/heads/master/goldmane/proto/api.proto -o grpc_libs/api.proto
```

```bash
python -m grpc_tools.protoc --proto_path=./grpc_libs --python_out=grpc_libs/. --pyi_out=grpc_libs/. --grpc_python_out=grpc_libs/. grpc_libs/api.proto
```

```bash
kubectl get cm -n calico-system goldmane-ca-bundle -o jsonpath="{.data.tigera-ca-bundle\.crt}" > certs/goldmane-ca.crt
```

```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.crt}" | base64 -d > certs/goldmane.crt
```

```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.key}" | base64 -d > certs/goldmane.key
```






### Self sign?
```bash
kubectl get secret -n tigera-operator tigera-ca-private -o json -o=jsonpath="{.data.tls\.crt}" | base64 -d > certs/operator.crt
kubectl get secret -n tigera-operator tigera-ca-private -o json -o=jsonpath="{.data.tls\.key}" | base64 -d > certs/operator.key
```

```
openssl req \
  -newkey rsa:2048 -nodes -sha256 -keyout certs/domain.key \
  -subj '/CN=goldmane/O=We love Calico/C=US' \
  -addext "subjectAltName=IP:172.19.0.2,IP:172.19.0.3,IP:172.19.0.4,IP:172.19.0.5,IP:172.18.0.2,IP:172.18.0.3,IP:172.18.0.4,IP:172.18.0.5" \
  -out certs/domain.csr 
```

```
openssl x509 -req \
    -in certs/domain.csr \
    -CA certs/operator.crt -CAkey certs/operator.key \
    -out certs/domain.crt \
    -days 1024 \
    -sha256 -extensions v3_req -extfile certs/req.conf
```