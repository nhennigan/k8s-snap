# How to use Ceph storage with Canonical K8s

[Ceph] can be used to hold Kubernetes persistent volumes and is the recommended
storage solution for {{product}}. Distributed, redundant storage is a must-have when you want to develop reliable applications. The ``ceph-csi`` plugin automatically provisions and attaches the Ceph volumes
to Kubernetes workloads. This how-to guide is adapted from
[block-devices-and-kubernetes].


`````{tab-set}
:sync-group: category

````{tab-item} For the snap
:sync: snap
## What you'll need

This guide assumes the following:

- You have root or sudo access to the machine
- You have a bootstrapped {{product}} cluster (see the
  [getting-started-guide])
- You have a running Ceph cluster

## Create a Ceph storage pool

Create a storage pool named "kubernetes" in the Ceph cluster.

We will set the number of placement groups to 128 because the Ceph cluster of
this demonstration will have less than 5 OSDs. (See [placement groups])

```
ceph osd pool create kubernetes 128
```

Initialise the pool as a Ceph block device pool.

```
rbd pool init kubernetes
```

## Configure ceph-csi

Ceph CSI is the Container Storage Interface (CSI) driver for Ceph. With Ceph
CSI, Kubernetes will be able to accomplish tasks related to your Ceph cluster
(like attaching volumes to workloads.)

The following command creates a user called "kubernetes" with the necessary
capabilities to administer your Ceph cluster:

```
ceph auth get-or-create client.kubernetes mon 'profile rbd' osd 'profile rbd pool=kubernetes' mgr 'profile rbd pool=kubernetes'
```

For more information on user capabilities in Ceph, see the [authorisation capabilities page][]

```
[client.kubernetes]
	key = AQBh1TNmFYERJhAAf5yqP4Wnrb/u4yNGsBKZHA==
```

Note the generated key, you will need it at a later step.

## Generate csi-config-map.yaml

First, get the `fsid` and the monitor addresses of your cluster.

```
sudo ceph mon dump
```

This will dump a Ceph monitor map such as:

```
epoch 2
fsid 6d5c12c9-6dfb-445a-940f-301aa7de0f29
last_changed 2024-05-02T14:01:37.668679-0400
created 2024-05-02T14:01:35.010723-0400
min_mon_release 18 (reef)
election_strategy: 1
0: [v2:10.0.0.136:3300/0,v1:10.0.0.136:6789/0] mon.dev
dumped monmap epoch 2
```

Keep note of the v1 IP (`10.0.0.136:6789`) and the `fsid`
(`6d5c12c9-6dfb-445a-940f-301aa7de0f29`) as you will need to refer to them soon.

```
cat <<EOF > csi-config-map.yaml
---
apiVersion: v1
kind: ConfigMap
data:
  config.json: |-
    [
      {
        "clusterID": "fsid 6d5c12c9-6dfb-445a-940f-301aa7de0f29",
        "monitors": [
          "10.0.0.136:6789",
        ]
      }
    ]
metadata:
  name: ceph-csi-config
EOF
```

Then apply:

```
kubectl apply -f csi-config-map.yaml
```

Recent versions of ceph-csi also require an additional ConfigMap object to
define Key Management Service (KMS) provider details. KMS is not set up as part
of this guide, hence put an empty configuration in `csi-kms-config-map.yaml`.

```
cat <<EOF > csi-kms-config-map.yaml
---
apiVersion: v1
kind: ConfigMap
data:
  config.json: |-
    {}
metadata:
  name: ceph-csi-encryption-kms-config
EOF
```

Then apply:

```
kubectl apply -f csi-kms-config-map.yaml
```

If you do need to configure a KMS provider, an [example ConfigMap][] is available
in the Ceph repository.

Create the `ceph-config-map.yaml` which will be stored inside a `ceph.conf` file
in the CSI containers. This `ceph.conf` file will be used by Ceph daemons on
each container to authenticate with the Ceph cluster.

```
cat <<EOF > ceph-config-map.yaml
---
apiVersion: v1
kind: ConfigMap
data:
  ceph.conf: |
    [global]
    auth_cluster_required = cephx
    auth_service_required = cephx
    auth_client_required = cephx
  # keyring is a required key and its value should be empty
  keyring: |
metadata:
  name: ceph-config
EOF
```

Then apply:

```
kubectl apply -f ceph-config-map.yaml
```

## Create the ceph-csi cephx secret

This secret contains the `userID` and `userKey` created in the Ceph cluster
earlier.

```
cat <<EOF > csi-rbd-secret.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: csi-rbd-secret
  namespace: default
stringData:
  userID: kubernetes
  userKey: AQBh1TNmFYERJhAAf5yqP4Wnrb/u4yNGsBKZHA==
EOF
```

Then apply:

```
kubectl apply -f csi-rbd-secret.yaml
```

## Create ceph-csi custom Kubernetes objects

Create the ServiceAccount and RBAC ClusterRole/ClusterRoleBinding objects:

```
kubectl apply -f https://raw.githubusercontent.com/ceph/ceph-csi/master/deploy/rbd/kubernetes/csi-provisioner-rbac.yaml

kubectl apply -f https://raw.githubusercontent.com/ceph/ceph-csi/master/deploy/rbd/kubernetes/csi-nodeplugin-rbac.yaml
```

Create the ceph-csi provisioner and node plugins:

```
wget https://raw.githubusercontent.com/ceph/ceph-csi/master/deploy/rbd/kubernetes/csi-rbdplugin-provisioner.yaml
:
kubectl apply -f csi-rbdplugin-provisioner.yaml

wget https://raw.githubusercontent.com/ceph/ceph-csi/master/deploy/rbd/kubernetes/csi-rbdplugin.yaml

kubectl apply -f csi-rbdplugin.yaml
```

Consider this important note from the Ceph documentation:

> The provisioner and node plugin YAMLs will, by default, pull the development
> release of the ceph-csi container (quay.io/cephcsi/cephcsi:canary). The YAMLs
> should be updated to use a release version container for production workloads.

## Create a StorageClass

You are ready to create a ceph-csi StorageClass.

```
cat <<EOF > csi-rbd-sc.yaml
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
   name: csi-rbd-sc
provisioner: rbd.csi.ceph.com
parameters:
   clusterID: b9127830-b0cc-4e34-aa47-9d1a2e9949a8
   pool: kubernetes
   imageFeatures: layering
   csi.storage.k8s.io/provisioner-secret-name: csi-rbd-secret
   csi.storage.k8s.io/provisioner-secret-namespace: default
   csi.storage.k8s.io/controller-expand-secret-name: csi-rbd-secret
   csi.storage.k8s.io/controller-expand-secret-namespace: default
   csi.storage.k8s.io/node-stage-secret-name: csi-rbd-secret
   csi.storage.k8s.io/node-stage-secret-namespace: default
reclaimPolicy: Delete
allowVolumeExpansion: true
mountOptions:
   - discard
EOF
```

Then apply:

```
kubectl apply -f csi-rbd-sc.yaml
```

## Create a Persistent Volume Claim (PVC) for a RBD-backed file-system

This PVC will allow users to request RBD-backed storage.

```
cat <<EOF > pvc.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rbd-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 1Gi
  storageClassName: csi-rbd-sc
EOF
```

Then apply:

```
kubectl apply -f pvc.yaml
```

## Create a pod that binds to the RADOS Block Device PVC

Finally, create a pod configuration that uses the RBD-backed PVC.

```
cat <<EOF > pod.yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: csi-rbd-demo-pod
spec:
  containers:
    - name: web-server
      image: nginx
      volumeMounts:
        - name: mypvc
          mountPath: /var/lib/www/html
  volumes:
    - name: mypvc
      persistentVolumeClaim:
        claimName: rbd-pvc
        readOn
EOF
```

Then apply:

```
kubectl apply -f pod.yaml
```

## Verify that the pod is using the RBD PV

To verify that the `csi-rbd-demo-pod` is indeed using a RBD Persistent Volume, run
the following commands, you should see information related to attached volumes
in both of their outputs:

```
kubectl describe pvc rbd-pvc

kubectl describe pod csi-rbd-demo-pod
```

````

````{tab-item} For the charm
:sync: charm

## What you'll need

This guide assumes that you have an existing {{product}} cluster.
See the [charm installation] guide for more details.

In case of localhost/LXD Juju clouds, please make sure that the K8s units are
configured to use VM containers with Ubuntu 22.04 as the base and adding the
``virt-type=virtual-machine`` constraint. In order for K8s to function properly,
an adequate amount of resources must be allocated:

```{literalinclude} ../../_parts/install.md
:start-after: <!-- juju vm start -->
:end-before: <!-- juju vm end -->
```

## Deploying Ceph

Deploy a Ceph cluster containing one monitor and three storage units
(OSDs). In this example, a limited amount of reources is being allocated.

```
juju deploy -n 1 ceph-mon \
    --constraints "cores=2 mem=4G root-disk=16G" \
    --config monitor-count=1
juju deploy -n 3 ceph-osd \
    --constraints "cores=2 mem=4G root-disk=16G" \
    --storage osd-devices=1G,1 --storage osd-journals=1G,1
juju integrate ceph-osd:mon ceph-mon:osd
```

If using LXD, configure the OSD units to use VM containers by adding the
constraint: ``virt-type=virtual-machine``.

Once the units are ready, deploy ``ceph-csi``. By default, this enables
the ``ceph-xfs`` and ``ceph-ext4`` storage classes, which leverage
Ceph RBD.

```
juju deploy ceph-csi --config provisioner-replicas=1
juju integrate ceph-csi k8s:ceph-k8s-info
juju integrate ceph-csi ceph-mon:client
```

CephFS support can optionally be enabled:

```
juju deploy ceph-fs
juju integrate ceph-fs:ceph-mds ceph-mon:mds
juju config ceph-csi cephfs-enable=True
```

## Validating the CSI integration

Ensure that the storage classes are available and that the
CSI pods are running:

```
juju ssh k8s/leader -- sudo k8s kubectl get sc,po --namespace default
```

The list should include the ``ceph-xfs`` and ``ceph-ext4`` storage classes as
well as ``cephfs``, if it was enabled.

Verify that Ceph PVCs work as expected. Connect to the k8s leader unit
and define a PVC like so:

```
juju ssh k8s/leader

cat <<EOF > /tmp/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: raw-block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Filesystem
  resources:
    requests:
      storage: 64Mi
  storageClassName: ceph-xfs
EOF

sudo k8s kubectl apply -f /tmp/pvc.yaml
```

Next, create a pod that writes to a Ceph volume:

```
cat <<EOF > /tmp/writer.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pv-writer-test
  namespace: default
spec:
  restartPolicy: Never
  volumes:
  - name: pvc-test
    persistentVolumeClaim:
      claimName: raw-block-pvc
  containers:
  - name: pv-writer
    image: busybox
    command: ["/bin/sh", "-c", "echo 'PVC test data.' > /pvc/test_file"]
    volumeMounts:
    - name: pvc-test
      mountPath: /pvc
EOF

sudo k8s kubectl apply -f /tmp/writer.yaml
```

If the pod completes successfully, our Ceph CSI integration is functional.

```
sudo k8s kubectl wait pod/pv-writer-test \
    --for=jsonpath='{.status.phase}'="Succeeded" \
    --timeout 2m
```

`````

Congratulations! By following this guide, you've set up a basic yet reliable
persistent storage solution for your Kubernetes cluster. To further enhance and
prepare your cluster for production use, we recommend reviewing the official
Ceph documentation: [Intro to Ceph].

<!-- LINKS -->

[Ceph]: https://ceph.io/
[getting-started-guide]: ../../tutorial/getting-started.md
[block-devices-and-kubernetes]: https://docs.ceph.com/en/latest/rbd/rbd-kubernetes/
[placement groups]: https://docs.ceph.com/en/mimic/rados/operations/placement-groups/
[Intro to Ceph]: https://docs.ceph.com/en/latest/start/
[authorisation capabilities page]:[https://docs.ceph.com/en/latest/rados/operations/user-management/#authorization-capabilities]
[example ConfigMap]:https://github.com/ceph/ceph-csi/blob/devel/examples/kms/vault/kms-config.yaml

[charm installation]: ./charm
[Ceph]: https://docs.ceph.com/
