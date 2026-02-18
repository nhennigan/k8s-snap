# How to upgrade {{product}}

Upgrading the Kubernetes version of a node is a critical operation that
requires careful planning and execution. Keeping up-to-date ensures you have the latest bug-fixes
and security patches for smooth operation of your cluster.
This how-to guide will cover the steps to upgrade the {{product}}
and how to put a hold on upgrades if desired.

```{note} Kubernetes will not automatically handle minor
release upgrades. The cluster will not perform an unattended
automatic upgrade between minor versions, e.g. 1.30.1 to 1.31.0 regardless of the instalation method.
Attended upgrades are required when you wish to upgrade to a minor version.
```

## Important considerations before upgrading

- According to the [upstream Kubernetes], skipping **minor** versions while
upgrading is not supported. For more details, please visit the
[Version Skew Policy].
- As with all upgrades, there is a possibility that there may be
unforeseen difficulties. It is highly recommended to make
a backup of any important data, including any running workloads.
For more details on creating backups, see the separate
[docs on backups][backup-restore].

Before upgrading, verify that:

* Your cluster is running normally
* Your Juju client and controller/models are running the same,
  stable version of Juju (see the [Juju docs][juju-docs]) if you are using the 
  charm 
* You read the [Upstream release notes][upstream-notes] for details
  of Kubernetes deprecation notices and API changes that may impact
  your workloads
* You have a target workload cluster if using CAPI and {{product}}
* `kubectl` installed and configured to access your management cluster.
* The workload cluster kubeconfig.

It is also important to understand that Kubernetes will only
upgrade and if necessary migrate, components relating specifically
to elements of Kubernetes installed and configured as part of Kubernetes.
This may not include any customized configuration of Kubernetes,
or non-built-in generated objects (e.g. storage classes) or deployments which
rely on deprecated APIs.

## Pre-upgrade steps 


`````{tab-set}

````{tab-item} Snap
:sync: key1

Determine which version of  {{product}} snap is currently deployed: 

```
snap info k8s | grep tracking
```

````

````{tab-item} Charm
:sync: key2
Determine which version of each application is currently deployed by running:

```sh
juju status
```
<!-- markdownlint-restore -->

The ‘App’ section of the output lists each application and its
version number. Note that this is the version of the upstream
application deployed. The version of the Juju charm is indicated
under the column titled ‘Rev’. The charms may be updated in
between new versions of the application.

<!-- markdownlint-disable -->
```
Model       Controller  Cloud/Region   Version  SLA          Timestamp
my-cluster  canonicaws  aws/us-east-1  3.6.0    unsupported  16:02:18-05:00

App      Version  Status  Scale  Charm    Channel        Rev  Exposed  Message
k8s      1.31.3   active      3  k8s      1.31/stable    123  yes      Ready

Unit        Workload  Agent  Machine  Public address  Ports     Message
k8s/0       active    idle   0        54.89.153.117   6443/tcp  Ready
k8s/1*      active    idle   1        3.238.230.3     6443/tcp  Ready
k8s/2       active    idle   2        34.229.202.243  6443/tcp  Ready

Machine  State    Address         Inst id              Base          AZ          Message
0        started  54.89.153.117   i-0b6fc845c28864913  ubuntu@22.04  us-east-1f  running
1        started  3.238.230.3     i-05439714c88bea35f  ubuntu@22.04  us-east-1f  running
2        started  34.229.202.243  i-07ecf97ed29860334  ubuntu@22.04  us-east-1c  running
```
<!-- markdownlint-restore -->
````

````{tab-item} CAPI
:sync: key3

Prior to the upgrade, ensure that the management cluster is in a healthy
state.

```
kubectl get nodes -o wide
```

Confirm the Kubernetes version of the workload cluster:

```
kubectl --kubeconfig c1-kubeconfig.yaml get nodes -o wide
```
````

`````

## Patch upgrade

Patch upgrades address bug fixes and are typically safe, introducing no
breaking changes.

### List available revisions 

`````{tab-set}

````{tab-item} Snap
:sync: key1
Snaps automatically check for updates of their specific track
(e.g. `1.35-classic`) several times a day and apply them when available.
These updates ensure that the latest changes in the installed track are applied.
Patch upgrades can also be triggered manually by following the steps below.

```
snap info k8s 
```

````

````{tab-item} Charm
:sync: key2
Juju will contact [Charmhub] daily to find new revisions of charms
deployed in your models. To see if the `k8s` or `k8s-worker` charms
can be upgraded, set with the following:

```sh
juju status --format=json | \
   jq '.applications |
        to_entries[] | {
           application: .key,
           "charm-name": .value["charm-name"],
           "charm-channel": .value["charm-channel"],
           "charm-rev": .value["charm-rev"],
           "can-upgrade-to": .value["can-upgrade-to"]
        }'
```

This outputs a list of applications in the model:

* the name of the application (ex. `k8s`)
* the charm used by the application (ex. `k8s`)
* the kubernetes channel this charm follows (ex. `1.31/stable`)
* the current charm revision  (ex. `1001`)
* the next potential charm revision (ex. `ch:amd64/k8s-1002`)

If the `can-upgrade-to` revision is `null`, the charm is on the most
stable release within this channel.
````

````{tab-item} CAPI
:sync: key3
TODO 
Determine which version of  {{product}} snap is currently deployed: 

```
snap info k8s | grep tracking
```
````

`````


### Refresh {{product}}

`````{tab-set}

````{tab-item} Snap
:sync: key1
```
snap refresh k8s
```

````

````{tab-item} Charm
:sync: key2
Before running an upgrade, check that the cluster is
steady and ready for upgrade. The charm will perform checks
necessary to confirm the cluster is in safe working order before
upgrading.

```sh
juju run k8s/leader pre-upgrade-check
```

If no error appears, the `pre-upgrade-check` completed successfully.


#### Control Plane units (k8s)

Following the `pre-upgrade-check` update the control-plane nodes.

```sh
juju refresh k8s
juju status k8s --watch 5s
```

The `refresh` command instructs the juju controller to use the new charm
revision within the current charm `channel`. The charm code is simultaneously
replaced on each unit, then the `k8s` snap is updated unit-by-unit in order
to maintain a highly-available kube-api-server endpoint, starting with the
Juju leader unit for the application.

During the upgrade process, the application status message and the
`k8s` leader unit message will display the current progress,
listing the `k8s` and `k8s-worker` units still pending upgrades.

After the `k8s` charm is upgraded, the application `Version` from `juju status`
will reflect the updated version of the control-plane nodes making up the
cluster.

#### Worker units (k8s-worker)

After updating the control-plane applications, worker nodes may be upgraded
by running the `pre-upgrade-check` action.

```sh
juju run k8s-worker/leader pre-upgrade-check
juju refresh k8s-worker
juju status k8s-worker --watch 5s
```

The `refresh` command instructs the juju controller to use the new charm
revision of the application's charm channel to upgrade each unit. The
charm code is simultaneously replaced on each unit, then the `k8s`
snap is updated unit-by-unit starting with the Juju leader unit for the
application.

After the `k8s-worker` charm is upgraded, the application `Version` from
`juju status`
will reflect the updated version of the worker nodes making up the cluster.

```{note} Repeat [this section](#worker-units-k8s-worker) for every
application using the k8s-worker charm, if multiple k8s-worker
applications appear in the same model.
```

````

````{tab-item} CAPI
:sync: key3

In this step, annotate the Machine resource with
the in-place upgrade annotation. In this example, the machine
is called `c1-control-plane-xyzbw`.

```
kubectl annotate machine c1-control-plane-xyzbw "v1beta2.k8sd.io/in-place-upgrade-to=<upgrade-option>"
```

`<upgrade-option>` can be one of:

* `channel=<snap-channel>` which refreshes k8s to the given snap channel.
  e.g. `channel=1.30-classic/stable`
* `revision=<revision>` which refreshes k8s to the given revision.
  e.g. `revision=123`
* `localPath=<path>` which refreshes k8s with the snap file from
  the given absolute path. e.g. `localPath=full/path/to/k8s.snap`

Please refer to the [ClusterAPI Annotations Reference][annotations-reference]
for further details on these options.

#### Monitor the in-place upgrade

Watch the status of the in-place upgrade for the machine,
by running the following command and checking the
`v1beta2.k8sd.io/in-place-upgrade-status` annotation:

```
kubectl get machine c1-control-plane-xyzbw -o yaml
```

On a successful upgrade:

* Value of the `v1beta2.k8sd.io/in-place-upgrade-status` annotation
  will be changed to `done`
* Value of the `v1beta2.k8sd.io/in-place-upgrade-release` annotation
  will be changed to the `<upgrade-option>` used to perform the upgrade.

#### Cancel a failing upgrade

The upgrade is retried periodically if the operation was unsuccessful.

The upgrade can be canceled by running the following commands
that remove the annotations:

```
kubectl annotate machine c1-control-plane-xyzbw "v1beta2.k8sd.io/in-place-upgrade-to-"
kubectl annotate machine c1-control-plane-xyzbw "v1beta2.k8sd.io/in-place-upgrade-change-id-"
```

````

`````



### Verify the upgrade

`````{tab-set}

````{tab-item} Snap
:sync: key1

Ensure that the upgrade was successful by checking the version of the snap and
confirming that the cluster is ready:

```
snap info k8s
sudo k8s status --wait-ready
```
````

````{tab-item} Charm
:sync: key2
Once an upgrade is complete, confirm the successful upgrade by running:

<!-- markdownlint-disable -->
```sh
juju status
```
<!-- markdownlint-restore -->

... should indicate that all units are active/idle and the correct
version of **Kubernetes** is listed in the application's **Version**

It is recommended that you run a [cluster validation][cluster-validation]
to ensure that the cluster is fully functional.

````

````{tab-item} CAPI
:sync: key3

Confirm that the node is healthy and runs on the new Kubernetes version:

```
kubectl --kubeconfig c1-kubeconfig.yaml get nodes -o wide
```
````

`````

## Minor version upgrade

Minor versions add new features or deprecate existing features without
breaking changes.
To upgrade to a new minor version, the channel needs to be changed.


### List available channels

`````{tab-set}

````{tab-item} Snap
:sync: key1
```
snap info k8s
```
````

````{tab-item} Charm
:sync: key2
Juju will contact [Charmhub] daily to find new revisions of charms
deployed in your models. To see if the `k8s` or `k8s-worker` charms
can be upgraded, set with the following:

```sh
juju status --format=json | \
   jq '.applications |
        to_entries[] | {
           application: .key,
           "charm-name": .value["charm-name"],
           "charm-channel": .value["charm-channel"],
           "charm-rev": .value["charm-rev"],
           "can-upgrade-to": .value["can-upgrade-to"]
        }'
```

This outputs a list of applications in the model:

* the name of the application (ex. `k8s`)
* the charm used by the application (ex. `k8s`)
* the kubernetes channel this charm follows (ex. `1.31/stable`)
* the current charm revision  (ex. `1001`)
* the next potential charm revision (ex. `ch:amd64/k8s-1002`)

If the `can-upgrade-to` revision is `null`, the charm is on the most
stable release within this channel.  Continue with the
[Pre Upgrade Check](#the-pre-upgrade-check).

Otherwise, complete the [Upgrade Patch](upgrade-patch) instructions first.
````

````{tab-item} CAPI
:sync: key3

CAPI upgrades is the same process as the patch version so follow those instructions
````

`````

### Check version specific instructions and possible manual steps

Please check [Upgrade notes] for any version-specific considerations or manual
steps before upgrading.


### Change the channel

The {{product}} snap channel can be changed by using the `snap refresh`
command.

`````{tab-set}

````{tab-item} Snap
:sync: key1

```
snap refresh --channel=1.35-classic/stable k8s
```

````

````{tab-item} Charm
:sync: key2
Before running an upgrade, check that the cluster is
steady and ready for upgrade. The charm will perform checks
necessary to confirm the cluster is in safe working order before
upgrading.

```sh
juju run k8s/leader pre-upgrade-check
```

If no error appears, the `pre-upgrade-check` completed successfully.

#### Control Plane units (k8s)

Following the `pre-upgrade-check` update the control-plane nodes.

```sh
juju refresh k8s --channel ${NEXT_CHANNEL}
juju status k8s --watch 5s
```

The `refresh` command instructs the juju controller to follow a new
charm `channel`. The Kubernetes charm will be upgraded to the latest
revision within that channel. The charm code is simultaneously replaced
on each unit, then the `k8s` snap is updated unit-by-unit in order to
maintain a highly-available kube-api-server endpoint, starting with the
Juju leader unit for each application.

During the upgrade process, the application status message and the
`k8s` leader unit message will display the current progress,
listing the `k8s` and `k8s-worker` units still pending upgrades.

After the `k8s` charm is upgraded, the application `Version` from `juju status`
will reflect the updated version of the control-plane nodes making up the
cluster.

#### Worker units (k8s-worker)

After updating the control-plane applications, worker nodes may be upgraded
by running the `pre-upgrade-check` action.

```sh
juju run k8s-worker/leader pre-upgrade-check
juju refresh k8s-worker --channel ${NEXT_CHANNEL}
juju status k8s-worker --watch 5s
```

The `refresh` command instructs the juju controller to follow a new
charm channel related to the Kubernetes release and use the new charm
revision of the application's channel to upgrade each unit. The
charm code is simultaneously replaced on each unit, then the `k8s`
snap is updated unit-by-unit, starting with the Juju leader unit for the
application.

After the `k8s-worker` charm is upgraded, the application `Version`
from `juju status`
will reflect the updated version of the worker nodes making up the cluster.

```{note} Repeat [this section](#worker-units-k8s-worker) for every
application using the k8s-worker charm, if multiple k8s-worker
applications appear in the same model.
```

````

````{tab-item} CAPI
:sync: key3

CAPI upgrades is the same process as the patch version so follow those instructions
````

`````


### Verify the upgrade 

Ensure that the upgrade was successful by checking the version of the snap
and confirming that the cluster is ready:

`````{tab-set}

````{tab-item} Snap
:sync: key1
```
snap info k8s
sudo k8s status --wait-ready
```

````

````{tab-item} Charm
:sync: key2
Once an upgrade is complete, confirm the successful upgrade by running:

<!-- markdownlint-disable -->
```sh
juju status
```
<!-- markdownlint-restore -->

... should indicate that all units are active/idle and the correct
version of **Kubernetes** is listed in the application's **Version**

Run a [cluster validation][cluster-validation]
to ensure that the cluster is fully functional.

````

````{tab-item} CAPI
:sync: key3

CAPI upgrades is the same process as the patch version so follow those instructions
````

`````

```{note}
In a multi-node cluster, the upgrade should be performed on all nodes.
```

## Freeze upgrades - TODO make generic 

To prevent automatic updates, the snap can be tied to a specific revision.
`snap refresh --hold[=<duration>]` holds snap refreshes for a specified
duration (or forever, if no value is specified).

```
snap refresh k8s --hold
```

Or specify a time window:

```
snap refresh k8s --hold=24h
```

<!-- LINKS -->
[upstream Kubernetes]: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/
[Version Skew Policy]: https://kubernetes.io/docs/setup/release/version-skew-policy/
[backup guide]: ./backup-restore.md
[snap documentation]: https://snapcraft.io/docs/managing-updates
[Upgrade notes]: ../reference/upgrading

<!-- LINKS -->

[Kubernetes release page]: https://kubernetes.io/releases/
[backup-restore]:      ../../snap/howto/backup-restore
[Charmhub]:            https://charmhub.io/k8s
[cluster-validation]:  ./validate
[juju-docs]:           https://documentation.ubuntu.com/juju/3.6/howto/manage-models/md#deprecation
[version-skew-policy]: https://kubernetes.io/releases/version-skew-policy/

<!-- LINKS -->
[release-notes]:      /releases/charm/index
[upstream-notes]:     https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG

[getting-started]: ../tutorial/getting-started.md
[annotations-reference]: ../reference/annotations.md
