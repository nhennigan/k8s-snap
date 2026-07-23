# Install {{product}}

There's more than one way to install {{product}}. You'll find links to
the current How-to guides below.

<!-- **Make the common ones the same page - custom bootstrap, adding a worker just make it per deployment. Then have variations**

So side nav will look like 

snap 

charm 

capi 

custom bootstrap 

worker 

lxd 


air gapped 

dev env etc ...

So we will be linking to the same page more than once as it appears across the types -->

```{toctree}
:glob:
:titlesonly:
:hidden:

k8s snap <snap.md>
k8s charm <charm.md>
k8s CAPI <provision.md>
Custom bootstrap config <custom-bootstrap-config.md>
Add a worker <custom-worker.md>
LXD <lxd.md>
Multipass <multipass.md>
Air-gapped environments <offline.md>
FIPS mode <fips.md>
DISA STIG hardened cluster <disa-stig.md>
Terraform <install-terraform.md>
Uninstall <uninstall.md>
```

## Snap 

- [k8s snap](snap.md)
- [Custom bootstrap configuration](custom-bootstrap-config)
- [Add a worker](custom-worker.md)
- [LXD](lxd.md)
- [Multipass](multipass)
- [Air-gapped environments](offline.md)
- [Development environments](dev-env.md)
- [FIPS mode](fips.md)
- [DISA STIG hardened cluster](disa-stig.md)
- [Uninstall the snap](uninstall.md)

## Charm 

- [k8s charm](charm.md)
- [Custom configuration](install-custom.md)
- [Add a worker](custom-workers.md)
- [LXD](install-lxd.md)
- [Terraform](install-terraform.md)

## CAPI 

- [Provision a Canonical Kubernetes cluster](provision)
- [Use custom bootstrap configuration](custom-bootstrap-config)
- [Install custom Canonical Kubernetes](custom-ck8s)
