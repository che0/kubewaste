kubewaste
=========

Displays how much resources are you currently wasting in your Kubernetes pods. Compares CPU and memory requests to current usage.


How to use
----------

```
$ ./kubewaste --context my-k8s --namespace playground
POD                                   CONTAINER            CPU_REQ    CPU_USED    CPU_PCT    MEM_REQ    MEM_USED    MEM_PCT
control-6c64f6f987-7vvg4              control-api          1000m      1m          0.1%       2048Mi     15Mi        0.7%
control-6c64f6f987-7vvg4              control-proxy        100m       0m          0.4%       128Mi      11Mi        8.4%
aggregator-sandbox-6b9fc97d4c-znbx7   aggregator-sandbox   1000m      112m        11.2%      1024Mi     81Mi        7.9%
k8s-importer-7bf7bc94f8-sfxbq         importer             10m        0m          4.3%       96Mi       64Mi        66.4%
logging-api-86d4ff48b8-dvtr6          logging-api          100m       0m          0.1%       50Mi       14Mi        27.1%
logstash-queue-dev-8dbff5c77-n4xkb    logstash             1000m      5m          0.5%       5120Mi     4191Mi      81.9%
logstash-queue-dev-8dbff5c77-n4xkb    logstash-exporter    100m       0m          0.0%       10Mi       18Mi        178.1%
memcache-579b6c8b6b-fqlvr             mc                   1000m      0m          0.0%       1024Mi     6Mi         0.6%
```


Questions
---------

* **I'm getting `[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1001)`**
Your `~/.kube/config` file probably does not have correct CA for your cluster. You can fix it by adding the proper config item:

```yaml
- name: my-k8s
  cluster:
    server: https://my-k8s.whatever.example.com:443
    certificate-authority: /usr/local/share/my-cool-ca/ca.pem
```

* **How can I sort the output?**
Pipe it through `sort`.
