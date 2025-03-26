```bash
curl -L https://raw.githubusercontent.com/projectcalico/calico/refs/heads/master/goldmane/proto/api.proto -o api.proto
```

```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.crt}" | base64 -d > ../certs/goldmane.crt
```

```bash
kubectl -n calico-system get secret goldmane-key-pair -o json -o=jsonpath="{.data.tls\.key}" | base64 -d > ../certs/goldmane.key
```