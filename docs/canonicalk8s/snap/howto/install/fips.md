# How to install a FIPS compliant Kubernetes cluster

```{versionadded} release-1.34
```

<!-- SPREAD 
# Tear down FIPS settings on exit
trap 'sudo pro disable fips-updates --assume-yes; sudo pro detach --assume-yes; sudo rm -f /root/pro /root/enabled /root/fips' EXIT
# Start doc test
-->

<!-- SPREAD SUITE: snap_clean -->

The [Federal Information Processing Standard (FIPS) 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) is a US government
security standard regulating the use of cryptography. Compliance is crucial for
US government and regulated industries. This how-to guide provides the steps to
set up a FIPS compliant Kubernetes cluster using the {{ product }} snap.

## Prerequisites

This guide assumes the following:

- Ubuntu 22.04 machine with at least 8GB of RAM and 40 GB disk storage
- You have root or sudo access to the machine
- Internet access on the machine

```{note}
Canonical K8s uses the core22 base snap which includes certified crypto
libraries from Ubuntu 22.04. Strictly speaking FIPS compliance requires
deploying on a matching certified kernel (Ubuntu 22.04). In practice auditors
sometimes accept mixing different kernel and user space library versions as long
as both are certified. From a technical perspective, FIPS mode should work on
other OS versions just like the k8s snap.
```

## Enable FIPS

To enable FIPS on your host machine, you must have an [Ubuntu Pro](https://ubuntu.com/pro)
subscription. Open the [Ubuntu Pro subscription dashboard](https://ubuntu.com/pro/dashboard) to retrieve your
Ubuntu Pro token required to enable access to FIPS-certified modules on your
system.

Ensure that your Ubuntu Pro Client is installed and running at least 27.0:

```
pro version
```

<!-- SPREAD 
pro version | xargs -r -I{} dpkg --compare-versions "{}" ge 27.0
-->

If you have not installed the [Ubuntu Pro Client](https://documentation.ubuntu.com/pro-client/en/latest/tutorials/basic_commands/#tutorial-commands) yet or have an older version,
run:

```
sudo apt update
sudo apt install ubuntu-pro-client
```

Attach the Ubuntu Pro token with the `--no-auto-enable` option to prevent
Canonical Livepatch services, which are not supported with FIPS:

<!-- SPREAD SKIP -->

```
sudo pro attach <your_pro_token> --no-auto-enable
```

<!-- SPREAD SKIP END -->

<!-- SPREAD
if [ ! -f /root/pro ]; then
    echo "Pro not yet attached"
    sudo touch /root/pro
    sync
    sudo pro attach C12wo2on4vvbA2PysZRQ78PyTHq9Y2 --no-auto-enable
fi
--> 

Now, enable the FIPS crypto modules on your host machine:

<!-- SPREAD SKIP -->

```
sudo pro enable fips-updates
```

<!-- SPREAD SKIP END -->

<!-- SPREAD 
if [ ! -f /root/enabled ]; then
    echo "FIPS not yet enabled"
    sudo touch /root/enabled
    sync
    echo "y" | sudo pro enable fips-updates
fi
-->

```{attention}
If you are deploying a [DISA STIG hardened cluster](disa-stig.md), you can skip
rebooting here since you will need reboot anyway after running `usg fix
disa_stig`. `/proc/sys/crypto/fips_enabled` will not update though until after
rebooting.
```

Reboot to apply the changes:

<!-- SPREAD SKIP -->

```
sudo reboot
```

<!-- SPREAD SKIP END -->

<!-- SPREAD
if [ ! -f /root/fips ]; then
    echo "FIPS reboot check"
    sudo touch /root/fips
    sync
    REBOOT
fi
-->

Verify your host machine is running in FIPS mode:

```
cat /proc/sys/crypto/fips_enabled
```

<!-- SPREAD 
cat /proc/sys/crypto/fips_enabled | grep 1
-->

If the output is `1`, your host machine is running in FIPS mode.

## Install dependencies

Install the [core22](https://snapcraft.io/core22) base snap containing the FIPS certified libraries from the
[`fips-updates` track](https://documentation.ubuntu.com/pro-client/en/latest/howtoguides/enable_fips).

```
sudo snap install core22 --channel=fips-updates/stable
```

If core22 is already installed, a message will be displayed:
`snap "core22" is already installed, see 'snap help refresh'`. In this case,
use the refresh command instead of install.

<!-- SPREAD SKIP -->

```
sudo snap refresh core22 --channel=fips-updates/stable
```

<!-- SPREAD SKIP END -->

## Install {{product}}

Install the {{ product }} snap on your FIPS host:

```{literalinclude} /_parts/install.md
:start-after: <!-- snap start -->
:end-before: <!-- snap end -->
```

<!-- SPREAD
sudo snap install k8s --classic --channel=1.35-classic/stable
-->

The components will automatically detect if the system is running in FIPS mode
and activate internal FIPS-related settings accordingly.

```{note}
Each node in the cluster must be installed following these instructions in
order for the whole cluster to be FIPS compliant.
```

## Next steps

```{attention}
If you are deploying a DISA STIG hardened cluster, stop here and instead
continue following the
[Canonical Kubernetes DISA STIG deployment guide](disa-stig.md)
to get detailed instructions on deploying with a stricter bootstrap or join
configuration file.
```

If this is the first node in your cluster, you can bootstrap it as usual:

```
sudo k8s bootstrap
```

Then you may wait for the node to be ready, by running:

```
sudo k8s status --wait-ready
```

Otherwise, you can [add it](/snap/tutorial/add-remove-nodes) to an existing cluster.

<!-- LINKS -->