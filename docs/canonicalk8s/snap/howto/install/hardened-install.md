# How to install {{ product }} with DISA STIG Hardening on a FIPS enabled machine

# How to set up a FIPS compliant Kubernetes cluster

[FIPS 140-3] (Federal Information Processing Standards) ensures security
compliance crucial for US government and regulated industries. This
how-to guide provides the steps to set up a FIPS compliant Kubernetes
cluster using the {{ product }} snap.

## Enable FIPS on an Ubuntu host machine

To enable FIPS on your host machine, you require an [Ubuntu Pro] subscription.
Open the [Ubuntu Pro subscription dashboard] to retrieve your Ubuntu Pro token
required to enable access to FIPS-certified modules on your system.

Ensure that your Ubuntu Pro Client is installed and running at
least 27.0:

```
pro version
```

If you have not installed the Ubuntu Pro Client yet or have an older version,
run:

```
sudo apt update
sudo apt install ubuntu-advantage-tools
```

Attach the Ubuntu Pro token with the `--no-auto-enable` option to prevent
Canonical Livepatch services, which are not supported with FIPS:

```
sudo pro attach <your_pro_token> --no-auto-enable
```

Now, enable the FIPS crypto modules on your host machine:

```
sudo pro enable fips-updates
```

Reboot to apply the changes:

```
sudo reboot
```

Verify your host machine is running in FIPS mode:

```
cat /proc/sys/crypto/fips_enabled
```

If the output is `1`, your host machine is running in FIPS mode.

``` {note}
If this section leaves open any further questions consult the [enable FIPS with Ubuntu]
guide for more detailed instructions.
```

## Firewall configuration for Kubernetes

{{ product }} requires certain firewall rules and guidelines to
ensure its operation. Additional firewall rules may also be necessary based on
user deployed workloads and services. Please follow the steps in the
[firewall configuration] guide.

## Ensure runtime with FIPS-certified libraries

Install the [core22] runtime with FIPS-certified libraries. The core22 snap
offers the fips-updates track, which contains NIST-certified packages along
with [security patches].

```
sudo snap install core22 --channel=fips-updates/stable
```

In case you have core22 already installed, perform a snap refresh to update it
to the latest version:

```
sudo snap refresh core22 --channel=fips-updates/stable
```

## Install Canonical Kubernetes

Install {{ product }} on your FIPS host:

```
sudo snap install k8s --classic
```

```{note}
Please note that FIPS is only available in the `k8s` release 1.34 and later.
If you are using an earlier version, you will need to upgrade to the latest
version of the snap to use FIPS support.
```

The k8s snap can leverage the host's FIPS compliant
cryptography. The components will automatically detect if the system is
running in FIPS mode and activate internal FIPS-related settings
accordingly.

After the snap installation completes, you can bootstrap the node as usual:

```
sudo k8s bootstrap
```

Then you may wait for the node to be ready, by running:

```
sudo k8s status
```

Your Kubernetes cluster is now ready for workload deployment and
additional node integrations. Please ensure that your workloads and
underlying system and hardware are FIPS compliant as well, to
maintain the security standards required by FIPS. For example,
ensure that your container images used for your applications can
be used with the hosts FIPS compliant libraries.


## Disable FIPS on an Ubuntu host machine

```{warning}
Disabling FIPS on a host machine is not recommended: only
enable FIPS on machines intended expressly to be used for FIPS.
Changing the FIPS mode may have implications for the
services running on your live cluster, so ensure you understand the
consequences of disabling FIPS before proceeding.
```

To disable FIPS on your host machine, run the following command:

```
sudo pro disable fips-updates
```

For further information on how to disable FIPS on the host,
consult the [disabling FIPS with Ubuntu] guide.

You can also change the [core22] snap back to the default
non-FIPS channel:

```
sudo snap refresh core22 --channel=latest/stable
```

Then reboot your host machine to apply the changes:

```
sudo reboot
```

After the reboot, the k8s snap's k8sd service will restart and
automatically detect that the host is no longer in FIPS mode
and will revert to the default non-FIPS settings.

<!-- LINKS -->
[FIPS 140-3]: https://csrc.nist.gov/pubs/fips/140-3/final
[Ubuntu Pro]: https://ubuntu.com/pro
[Ubuntu Pro subscription dashboard]: https://ubuntu.com/pro/dashboard
<!-- markdownlint-disable MD053 -->
[enable FIPS with Ubuntu]: https://ubuntu.com/tutorials/using-the-ubuntu-pro-client-to-enable-fips#1-overview
<!-- markdownlint-enable MD053 -->
[firewall configuration]: ../networking/ufw
[core22]: https://snapcraft.io/core22
[security patches]: <https://ubuntu.com/security/certifications/docs/16-18/fips-updates>
[disabling FIPS with Ubuntu]: https://documentation.ubuntu.com/pro-client/en/latest/howtoguides/enable_fips/#how-to-disable-fips


This guide iterates over the steps necessary to apply manual rules for
DISA STIG hardening to a {{ product }} cluster.

## Prerequisites

This guide assumes the following:

- Ubuntu machine with at least 4GB of RAM and 30 GB disk storage
- You have root or sudo access to the machine
- Internet access on the machine
- You have Ubuntu Pro enabled on your system. For more information, see
  [Ubuntu Pro documentation].

## DISA STIG host compliance
<!-- TODO: Ask Niamh if we should include this section -->

DISA STIG host compliance is achieved by running the [usg tool]
(`usg fix disa_stig`) that is also part
of the PRO tool set. To install the usg tool, run:

```
sudo apt update
sudo apt install usg
```

DISA STIG compliance for Ubuntu hosts can be achieved using the usg tool
installed above.

To generate a compliance audit report (without applying changes):

```
sudo usg audit disa_stig
```

```{warning}
The following command applies rule [V-270714] which will cause issues using
accounts with an empty password.
```

To automatically apply the recommended hardening changes:

```
sudo usg fix disa_stig
```

## Apply DISA Kubernetes STIG host rules

To comply with this guideline, the STIG templates we provide to bootstrap/join
nodes configure kubelet to run with the argument
`--protect-kernel-defaults=true`.

Configure the kernel as required for this setting by following the steps below:

```
sudo tee /etc/sysctl.d/99-kubelet.conf <<EOF
vm.overcommit_memory=1
vm.panic_on_oom=0
kernel.keys.root_maxbytes=25000000
kernel.keys.root_maxkeys=1000000
kernel.panic=10
kernel.panic_on_oops=1
EOF
sudo sysctl --system
```

```{note}
Please ensure that the configuration of `/etc/sysctl.d/99-kubelet.conf` is not
overridden by another higher order file.
```

## Deploy and bootstrap stig-compliant nodes

For your convenience, we have provided template configuration files that can be
used to configure Kubernetes service arguments that align with DISA STIG
requirements.

### Bootstrap the first control-plane node

To initialize the first control plane node with the necessary arguments for
disa-stig compliance, run:

```{literalinclude} ../../../_parts/install.md
:start-after: <!-- snap start -->
:end-before: <!-- snap end -->
```

```
sudo k8s bootstrap --file /var/snap/k8s/common/etc/templates/disa-stig/bootstrap.yaml
sudo k8s status --wait-ready
```

You can then optionally join additional control plane or worker nodes following
the sections below.

Through this configuration file, the following rules are applied:

- [V-242434] Kubernetes Kubelet must enable kernel protection
- [V-245541] Kubernetes Kubelet must not disable timeouts
- [V-242402] [V-242403] [V-242461] [V-242462] [V-242463] [V-242464]
  [V-242465] The Kubernetes API Server must have an audit log
  configured
- [V-254800] Kubernetes must have a Pod Security Admission control file
  configured
- [V-242400] The Kubernetes API server must have Alpha APIs disabled
- [V-254800] Kubernetes must have a Pod Security Admission control file
configured
- [V-242384] The Kubernetes Scheduler must have secure binding
- [V-242385] The Kubernetes Controller Manager must have secure binding

### Join additional control plane nodes

To join another control plane node to the cluster, first retrieve the join token
from an existing control plane node:

```
sudo k8s get-join-token <joining-node-hostname>
```

On the joining control plane node, run:

```{literalinclude} ../../../_parts/install.md
:start-after: <!-- snap start -->
:end-before: <!-- snap end -->
```

```
sudo k8s join-cluster --file=/var/snap/k8s/common/etc/templates/disa-stig/control-plane.yaml <join-token>
```

Through this configuration file, the following rules are applied:

- [V-242434] Kubernetes Kubelet must enable kernel protection
- [V-245541] Kubernetes Kubelet must not disable timeouts
- [V-242402] [V-242403] [V-242461] [V-242462] [V-242463] [V-242464]
  [V-242465] The Kubernetes API Server must have an audit log configured
- [V-254800] Kubernetes must have a Pod Security Admission control
  file configured
- [V-242400] The Kubernetes API server must have Alpha APIs disabled
- [V-254800] Kubernetes must have a Pod Security Admission control file
  configured
- [V-242384] The Kubernetes Scheduler must have secure binding
- [V-242385] The Kubernetes Controller Manager must have secure binding

### Join worker nodes

To join a worker node to the cluster, first retrieve the join token from an
existing control plane node:

```
sudo k8s get-join-token <joining-node-hostname> --worker
```

On the joining worker node, run:

```{literalinclude} ../../../_parts/install.md
:start-after: <!-- snap start -->
:end-before: <!-- snap end -->
```

```
sudo k8s join-cluster --file=/var/snap/k8s/common/etc/templates/disa-stig/worker.yaml <join-token>
```

Through this configuration file, the following rules are applied:

- [V-242434] Kubernetes Kubelet must enable kernel protection
- [V-245541] Kubernetes Kubelet must not disable timeouts

### Disable SSH on the Worker Nodes

If ssh is not needed to access the worker nodes it is recommended you disable
the ssh:

```
sudo systemctl disable ssh.service ssh.socket
```

```{note}
According to rule [V-242393] and [V-242394] Kubernetes Worker Nodes must not have
sshd service running or enabled. The host STIG rule [V-270665] on the other hand
expects sshd to be installed on the host. To comply with both rules, leave SSH
installed, but disable the service.
```

## Control Plane Alternative Configurations

### Kubernetes must have a Pod Security Admission control file configured

To comply with rule [V-254800], you must configure a Pod Security Admission
control file for your Kubernetes cluster. This file defines the Pod Security
Standards (PSS) that are enforced at the namespace level.

The STIG templates we provide to bootstrap/join nodes configure the Pod Security
admission controller to comply with these recommendations.

By default, the bootstrap configuration template will point to
`/var/snap/k8s/common/etc/configurations/pod-security-admission-baseline.yaml`,
which sets the pod security policy to “baseline”, a minimally restrictive policy
that prevents known privilege escalations.

This policy may be insufficient or impractical in some situations, in which case
the settings would need to be adjusted by doing one of the following:

1. Adjust the `--admission-control-config-file` path used when you
   bootstrap/join nodes to
   `/var/snap/k8s/common/etc/configurations/pod-security-admission-restricted.yaml`
   rather than the file above. This sets a more restrictive policy.
2. Edit
   `/var/snap/k8s/common/etc/configurations/pod-security-admission-baseline.yaml`
   to suit your needs based on the [upstream instructions].
3. Create your own audit policy based on the [upstream instructions] and adjust
   the `--admission-control-config-file` path used when you bootstrap/join
   nodes.

For more details, see the [Kubernetes Pod Security Admission documentation],
which provides an overview of Pod Security Standards (PSS), their enforcement
levels, and configuration options.

## The Kubernetes API Server must have an audit log configured

This applies to rules:

- [V-242402]
- [V-242403]
- [V-242461]
- [V-242462]
- [V-242463]
- [V-242464]
- [V-242465]

The STIG templates we provide to bootstrap/join nodes configure the Kubernetes
API servers audit settings and policy to comply with these recommendations.

By default, the bootstrap configuration template will point to
`/var/snap/k8s/common/etc/configurations/audit-policy.yaml`, which configures
logging of all (non-resource) events with request metadata, request body, and
response body as recommended by [V-242403].

This level of logging may be impractical for some situations, in which case the
settings would need to be adjusted and an exception put in place. To adjust the
audit settings, do one of the following:

1. Adjust the `--audit-policy-file` path used when you bootstrap/join nodes to
   use `/var/snap/k8s/common/etc/configurations/audit-policy-kube-system.yaml`
   rather than the file above. This configures the same level of logging but
   only for events in the kube-system namespace.
2. Edit `/var/snap/k8s/common/etc/configurations/audit-policy.yaml` to suit
   your needs based on the [upstream audit instructions] for this policy
   file.
3. Create your own audit policy based on the [upstream audit instructions]
   and adjust the `--audit-policy-file` path used when you bootstrap/join
   nodes to use it.

Canonical Kubernetes does not enable audit logging by default as it may incur
performance penalties in the form of increased disk I/O, which can lead to
slower response times and reduced overall cluster efficiency, especially under
heavy workloads.

## Next steps

Please assess your cluster for compliance using the [DISA STIG assessment page].
Review all findings and apply any necessary remediations to be fully DISA STIG
compliant. Be aware that some rules need to be upheld when you add workloads
to your cluster.

<!-- Links -->
[DISA STIG assessment page]: ../security/disa-stig-assessment.md
[usg tool]: https://documentation.ubuntu.com/security/docs/compliance/usg/
[Ubuntu Pro documentation]: https://documentation.ubuntu.com/pro/start-here/#start-here
[Kubernetes Pod Security Admission documentation]: https://kubernetes.io/docs/concepts/security/pod-security-admission/
[upstream instructions]: https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-admission-controller/
[upstream audit instructions]: https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/
[V-270714]: https://stigviewer.com/stigs/canonical_ubuntu_24.04_lts/2025-02-18/finding/V-270714
[V-270665]: https://stigviewer.com/stigs/canonical_ubuntu_24.04_lts/2025-02-18/finding/V-270665
[V-242403]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242403
[V-242434]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242434
[V-245541]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-245541
[V-254800]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-254800
[V-242402]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242402
[V-242461]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242461
[V-242462]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242462
[V-242463]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242463
[V-242464]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242464
[V-242465]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242465
[V-242400]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242400
[V-242384]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242384
[V-242385]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242385
[V-242393]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242393
[V-242394]: https://stigviewer.com/stigs/kubernetes/2025-02-20/finding/V-242394
