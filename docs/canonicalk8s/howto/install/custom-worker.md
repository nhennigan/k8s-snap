# How to join worker nodes with a custom configuration

When creating a {{ product }} cluster you may need to join a worker node with
a configuration that differs from the default. For example, the worker node
may need to use alternative certificates for security reasons or the worker
node may have specific networking requirements that must be configured at node
creation. Passing extra command line arguments or a configuration file
at cluster join allows you to modify the configuration of your worker node.

## k8s snap 

### Prerequisites

This guide assumes the following:

- A working Kubernetes cluster deployed with the `k8s` snap

### Generate worker join token

When generating a join token for a worker node, pass the `--worker`
parameter to the `get-join-token` command. Adding the
hostname when creating a worker join token is optional and is not included here.

```
sudo k8s get-join-token --worker
```

### Install the snap

On the new worker machine, install the snap:

```{literalinclude} ../../../_parts/install.md
:start-after: <!-- snap start -->
:end-before: <!-- snap end -->
```

### Join the cluster

#### Default configuration

To join the cluster with the default configuration, on the worker node use the
token generated from the output of the `get-join-token` command and run:

```
sudo k8s join-cluster <JOIN-TOKEN>
```

#### Command line arguments

To discover the configuration options available as command line arguments when
joining the cluster, on the control node run:

```
sudo k8s join-cluster --help
```

You can then run the join the cluster with the token generated from the output
of the `get-join-token` command and any arguments you may need. For example, to
set the output formatting to JSON run:

```
sudo k8s join-cluster --output-format=json <JOIN-TOKEN>
```

#### Configuration file

More configuration options are available when a configuration file is specified.
Please consult the {ref}`worker-node-join-config` reference page for all of the
available configuration options and their defaults.

In this example, the configuration file provided at cluster join will set
custom kubelet arguments on the worker machine.

Create a `custom_config.yaml` file that sets the intended custom configurations.

```
cat <<EOF > custom_config.yaml
extra-node-kubelet-args:
    "--max-pods" : "200"
EOF
```

On the worker node, join the cluster with the token generated from the output of
the `get-join-token` command and the `custom_config.yaml` file.

```
sudo k8s join-cluster --file path/to/custom_config.yaml <JOIN-TOKEN>
```

### Verify worker join

After a few moments, the node should have joined the cluster with a success
message. Verify the node has joined the cluster by switching to the control
node and running:

```
sudo k8s kubectl get nodes
```

The output should list the worker node in a `Ready` state.

Also verify if any custom configuration has been applied to the worker.

## k8s charm 


This guide will walk you through how to deploy multiple `k8s-worker`
applications with different configurations, to create node groups with specific
capabilities or requirements.

### Prerequisites

This guide assumes the following:

- A working Kubernetes cluster deployed with the `k8s` charm

### Example worker configuration

In this example, we will create two `k8s-worker` applications with different
configuration options.

```{note}
The configurations shown below are examples to demonstrate the deployment
pattern. You should adjust the node configurations, labels, and other
parameters according to your specific infrastructure requirements, workload
needs, and organizational policies. Review the [charm configuration] options
documentation to understand all available parameters that can be customized for
your worker nodes.
```

1. Workers for memory-intensive workloads (`worker-memory-config.yaml`):

```yaml
memory-workers:
  bootstrap-node-taints: "workload=memory:NoSchedule"
  kubelet-extra-args: "system-reserved=memory=2Gi"
```

2. Workers for GPU workloads (`worker-gpu-config.yaml`):

```yaml
gpu-workers:
  bootstrap-node-taints: "accelerator=nvidia:NoSchedule"
  node-labels: "gpu=true"
```

Deploy the worker applications with the custom configurations and integrate them
with the `k8s` application:

```bash
juju deploy k8s-worker memory-workers --base="ubuntu@24.04" --config ./worker-memory-config.yaml
juju integrate k8s memory-workers:cluster
juju integrate k8s memory-workers:containerd
juju integrate k8s memory-workers:cos-tokens

juju deploy k8s-worker gpu-workers --base="ubuntu@24.04" --config ./worker-gpu-config.yaml
juju integrate k8s gpu-workers:cluster
juju integrate k8s gpu-workers:containerd
juju integrate k8s gpu-workers:cos-tokens
```

Monitor the installation progress by running the following command:

```bash
juju status --watch 1s
```

<!-- LINKS -->
[charm configuration]: https://charmhub.io/k8s/configurations
