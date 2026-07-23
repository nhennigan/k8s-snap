# How to use custom bootstrap configuration

You may want to customize your deployment rather than use the deafult config - here is how you do it for the snap, charm and CAPI. 

## k8s snap 

When creating a {{ product }} cluster that differs from the default
configuration you can choose to use a custom bootstrap configuration.
The CLI interactive mode or a custom bootstrap configuration file allow you
to modify the configuration of the first node of your cluster.

### Configuration options

Please consult the [reference page] for all of the
available configuration options and their defaults.

``` {note}
Most of these configuration options are set during the initial bootstrapping
and cannot be modified afterward. Runtime changes may be unsupported and
could require deploying a new cluster. Refer to the reference page to
determine if an option allows later modifications.
```

### Interactive mode

The interactive mode allows for the selection of the built-in features, the pod
CIDR and the Service CIDR.

To bootstrap interactively, run:

<!-- SPREAD SKIP -->

```
sudo k8s bootstrap --timeout 10m --interactive
```

Here is an example custom configuration:

```
Which features would you like to enable? (network, dns, gateway, ingress, local-storage, load-balancer) [network, dns, gateway, local-storage]: network,ingress,dns
Please set the Pod CIDR: [10.1.0.0/16]: 10.1.0.0/16,fd01::/108
Please set the Service CIDR: [10.152.183.0/24]: 10.152.183.0/24,fd98::/108
```

The expected output shows your node's ip that will differ from this example:

```
Bootstrapping the cluster. This may take a few seconds, please wait.
Bootstrapped a new Kubernetes cluster with node address "192.122.3.111:6400".
The node will be 'Ready' to host workloads after the CNI is deployed successfully.
```

<!-- SPREAD SKIP END -->

### Bootstrap configuration file

If your deployment requires a more fine-tuned configuration, use the bootstrap
configuration file.

``` {note}
When using the custom configuration file on bootstrap, all features including
network, dns, gateway, ingress, load-balancer and local-storage are disabled
by default.
```

For this example, create a custom bootstrap configuration file that enables
the network feature:

```yaml
cat <<EOF > bootstrap.yaml
cluster-config:
  network:
    enabled: true
EOF
```

Then, apply the bootstrap configuration file:

<!-- SPREAD SKIP -->

```
sudo k8s bootstrap --file /path/to/bootstrap.yaml
```

<!-- SPREAD SKIP END -->

<!-- SPREAD
sudo k8s bootstrap --file bootstrap.yaml
sudo k8s status --wait-ready --timeout 3m
sudo k8s get network | grep "enabled: true"
-->

To verify any changes to the built-in features run:

```
sudo k8s status
```

<!-- LINKS -->

[reference page]: /snap/reference/config-files/bootstrap-config.md

## k8s charm 

### Prerequisites

This guide assumes the following:

- You have Juju installed on your system with your cloud credentials configured and a controller bootstrapped
- A Juju model is created and selected

### Create the configuration file

Before deploying the charm, create a YAML file with your desired configuration
options. Here's an example configuration, which for this guide we'll save as
`k8s-config.yaml`:

```yaml
k8s:
  # Specify the datastore type
  bootstrap-datastore: etcd

  # Configure pod and service CIDR ranges
  bootstrap-pod-cidr: "192.168.0.0/16"
  bootstrap-service-cidr: "10.152.183.0/24"

  # Enable required features
  dns-enabled: true
  gateway-enabled: true
  ingress-enabled: true
  metrics-server-enabled: true

  # Configure DNS settings
  dns-cluster-domain: "cluster.local"
  dns-upstream-nameservers: "8.8.8.8 8.8.4.4"

  # Add & Remove node-labels from the snap's default labels
  #   The k8s snap applies its default labels, these labels define what
  #   are added or removed from those defaults
  # <key>=<value> ensures the label is added to all the nodes of this application
  # <key>=-       ensures the label is removed from all the nodes of this application
  # See charm-configuration notes for more information regarding node labelling
  node-labels: >-
    environment=production
    node-role.kubernetes.io/worker=-
    zone=us-east-1

  # Configure local storage
  local-storage-enabled: true
  local-storage-reclaim-policy: "Retain"
```

You can find a full list of configuration options in the
[charm configurations] page.

```{note}
Remember that some configuration options can only be set during initial
deployment and cannot be changed afterward. Always review the
[charm configurations] documentation before deployment to ensure your settings
align with your requirements.
```

### Deploy the charm with custom configuration

Deploy the `k8s` charm with your custom configuration:

```{literalinclude} /_parts/install.md
:start-after: <!-- juju controlplane custom config start -->
:end-before: <!-- juju controlplane custom config end -->
```

### Bootstrap the cluster

Monitor the installation progress:

```bash
juju status --watch 1s
```

Wait for the unit to reach the `active/idle` state, indicating that the
{{product}} cluster is ready.

<!-- LINKS -->
[charm configurations]: https://charmhub.io/k8s/configurations

## CAPI 

The {{product}} bootstrap configuration gets automatically generated based on
user provided settings described in the [Cluster API configuration reference].

The configuration generated by the CAPI provider will also include CA
certificates as well as annotations and other settings that allow the provider
to function properly.

Not all bootstrap options are exposed through CAPI settings. However,
users can explicitly define the {{product}} bootstrap configuration.
This completely bypasses the other CAPI provider settings and the configuration
will be passed as-is to the {{product}} snap.

See the [Bootstrap configuration file reference] for more details about the
available settings.

### Pass the bootstrap configuration directly

The bootstrap configuration can be specified in the ``CK8sControlPlane`` spec:

```
apiVersion: controlplane.cluster.x-k8s.io/v1beta2
kind: CK8sControlPlane
metadata:
  name: c1-control-plane
  namespace: default
spec:
  machineTemplate:
    infrastructureTemplate:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      kind: DockerMachineTemplate
      name: c1-control-plane
  replicas: 1
  spec:
    bootstrapConfig:
      content: |
        cluster-config:
          annotations:
            k8sd/v1alpha/lifecycle/skip-cleanup-kubernetes-node-on-remove: "true"
            k8sd/v1alpha/lifecycle/skip-stop-services-on-remove: "true"
          network:
            enabled: true
          dns:
            enabled: true
          local-storage:
            enabled: true
            reclaim-policy: Retain
```

Note that the k8sd annotations allow the CAPI provider to properly remove
nodes.

### Use secrets to store the bootstrap configuration

The bootstrap configuration may contain sensitive data. For this reason, the
provider also allows passing it as a secret.

```
apiVersion: v1
kind: Secret
metadata:
  name: ck8s-bootstrap-config
type: Opaque
stringData:
  content: |
    cluster-config:
      annotations:
        k8sd/v1alpha/lifecycle/skip-cleanup-kubernetes-node-on-remove: "true"
        k8sd/v1alpha/lifecycle/skip-stop-services-on-remove: "true"
      network:
        enabled: true
      dns:
        enabled: true
      local-storage:
        enabled: true
        reclaim-policy: Retain
```

The secret can then be referenced like so:

```
apiVersion: controlplane.cluster.x-k8s.io/v1beta2
kind: CK8sControlPlane
metadata:
  name: c1-control-plane
  namespace: default
spec:
  machineTemplate:
    infrastructureTemplate:
      apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
      kind: DockerMachineTemplate
      name: c1-control-plane
  replicas: 1
  spec:
    bootstrapConfig:
      contentFrom:
        secret:
          # Name of the secret in the CK8sBootstrapConfig's namespace to use.
          name: ck8s-bootstrap-config
          # The key in the secret's data map for this value.
          key: content
```

<!-- LINKS -->
[Cluster API configuration reference]: /capi/reference/configs.md
[Bootstrap configuration file reference]: /snap/reference/config-files/bootstrap-config.md
