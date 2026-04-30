# Contribute to {{product}} development 

{{product}} is proudly open source, published under the GPLv3 license.
We welcome and encourage contributions to the code and the documentation. See
the [community page][] for ways to get in touch and provide feedback.

## Contribute to the code

{{product}} is shipped as a snap package. To contribute to the code,
you should first make sure you can build and test the snap locally.

### Build the snap

To build the snap locally, you will need the following:

- The latest, snap-based version of LXD (see the [install guide here][install
   lxd])
- The Snapcraft build tool, for building the snap (see the [Snapcraft
   documentation][]).

Clone the [GitHub repository for the k8s snap][code repo] and then open a
terminal in that directory. Run the command:

```
snapcraft --use-lxd
```

This will launch an LXD container and use it to build a version of the snap.
This will take some time as the build process fetches dependencies, stages the
‘parts’ of the snap and creates the snap package itself. The snap itself will
be fetched from the build environment and placed in the local project
directory. Note that the LXD container used for building will be stopped, but
not deleted. This is in case there were any errors or artifacts you may wish to
inspect.

### Install the snap

The snap can then be installed locally by using the `--dangerous` option. This
is a safeguard to make sure the user is aware that the snap is not signed by
the snap store, and is not confined:

```
sudo snap install k8s_v1.35.3_multi.snap --dangerous --classic
```

```{note} You will not be able to install this snap if there is already a
   k8s snap installed on your system.
```

```{note}
The snap may conflict with other software such as Docker or containerd,
which is why we recommend using a clean, isolated environment such as a
VM or LXD container.

See the [development env guide] if you'd rather install the snap directly
on your development machine.
```

Once you have verified the current snap build works, it can be removed with:

```
sudo snap remove k8s --purge
```

The `purge` option is recommended when iterating over code changes, as it also
removes all the installed artifacts which may be associated with the snap.

Now you can iterate over changes to the snap, rebuild and test.

As noted previously, the LXD container used for building is not removed and
will be reused by subsequent build instructions. When you are satisfied it is
no longer needed, this container can be removed:

```
lxc delete snapcraft-k8s
```

### Making a change to the API

The Canonical Kubernetes codebase references the `k8sd` and
`k8s-snap-api` package extensively. When contributing changes that
require API modifications, follow these steps:

1. Clone the `k8sd` and `k8s-snap-api` repositories from
   https://github.com/canonical/k8sd and
   https://github.com/canonical/k8s-snap-api

2. Add a module replace directive in your `k8sd/go.mod` file to point to
   your local API copy. For example:

```
module github.com/canonical/k8s

go 1.24.4

replace github.com/canonical/k8s-snap-api => /path/to/k8s-snap-api

require (
   ...
)
```

3. Make your API changes in the local copy.

4. Create a separate PR in the `k8s-snap-api` repository with your API changes.

5. Reference your `k8s-snap-api` PR in your main `k8s-snap` PR.

6. Once the k8s-snap-api PR is merged and tagged, remove the replace directive
   and update k8s-snap-api version in your k8s-snap PR

### Contribute changes

We welcome any improvements and bug-fixes to the {{product}} code.
Once you have tested your changes, please make a pull request on the [code
repository][code repo] and we will review it as soon as possible.

## PR review process

When you create your PR, a member of the team will review it. Your PR must
receive at least one approval from a Canonical Kubernetes team member before
it's eligible to be merged.

For faster reviews, ensure your PR:

* Passes all automated tests
* Has a clear title and description of the changes
* Links to related issues
* Includes test cases if relevant
* Contains only changes that are relevant to the PRs stated purpose
* Updates relevant documentation