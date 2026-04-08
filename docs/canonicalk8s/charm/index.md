---
myst:
  html_meta:
    description: "Explore the official Canonical Kubernetes charm documentation. Includes step-by-step tutorials, practical how-to guides, in-depth explanations, and technical reference."
---

# {{product}} charm documentation

```{toctree}
:hidden:
Overview <self>
```

```{toctree}
:hidden:
:titlesonly:
:caption: Deploy with Juju
tutorial/index.md
howto/index.md
explanation/index.md
reference/index.md
```

The {{product}} charm, `k8s`, is an operator-software which wraps an
application and contains all of the instructions necessary for deploying,
configuring, scaling, integrating the application on any cloud supported by
[Juju][].

The `k8s` charm takes care of installing and configuring the [k8s snap
package][] on cloud instances managed by Juju. Operating Kubernetes through
this charm makes it significantly easier to manage at scale, on remote cloud
instances and also to integrate other operators to enhance or customize your
Kubernetes deployment. You can find out more about {{product}} on the
[what is Canonical Kubernetes page][] or see a more detailed explanation in our 
[architecture documentation][arch].

## In this documentation 

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( tutorial/getting-started) • [What is Canonical Kubernetes?](/about)|
| **Deployment** | [`k8s` charms install](howto/install/charm) • [Terraform install](howto/install/install-terraform.md) • [Custom bootstap config install](howto/install/install-custom) • [Custom worker config install](howto/install/custom-workers) • [LXD VMs](howto/install/install-lxd) |
| **Networking** |  [Overview](explanation/networking) • [Ports and services](reference/ports-and-services) • [Proxy environment variables](reference/proxy.md) |
| **Security and compliance** |  [Explanation](explanation/security.md) • [Harden your cluster](howto/security/hardening) • [Report an issue](howto/report-security-issue.md) • [Custom registry](howto/custom-registry) |
| **Storage** | [Cluster datastore](reference/dqlite.md) |
| **Cluster management** | [Understanding upgrades](explanation/upgrade) • [Upgrade minor version](howto/upgrade-minor) • [Upgrade patch version](howto/upgrade-patch) • [Validate cluster upgrades](howto/validate) • [Node roles](explanation/roles) • [High availablity](explanation/high-availability) • [Clustering](explanation/clustering) • [Choose a channel](explanation/channels) • [Architecture](explanation/architecture)|
| **Troubleshooting** | [Troubleshoot your cluster](howto/troubleshooting) |
| **Configuration** | [Configure the cluster](howto/configure-cluster) • [Actions](reference/actions)  • [CharmHub links](reference/charms) • [Config files](reference/config-files/index) • [Availability zones](reference/az)|
| **Charm integrations** | [Openstack](charm/howto/openstack) • [etcd](charm/howto/etcd) • [Ceph CSI](charm/howto/ceph-csi) • [COS Lite](charm/howto/cos-lite.md) |

## How this documentation is organized

This documentation embodies the [Diátaxis framework].

- The [Tutorial](tutorial/getting-started) takes you step-by-step through 
  deploying your first {{product}} cluster.
- [How-to guides](howto/index) provide directions covering key cluster 
  operations and common tasks.
- [Reference](reference/index) contains technical definitions of APIs, 
  configuration and internal components.
- [Explanation](explanation/index) includes topic overviews, background and 
  context and detailed discussion.

## Project and community

{{product}} is a member of the Ubuntu family. It's an open source
project which welcomes community involvement, contributions, suggestions, fixes
and constructive feedback.

### Get involved

- [Canonical Kubernetes Slack]
- [Canonical Kubernetes Discourse]
- Our [community]
- How to [contribute]

### Releases 

- Our [release notes][releases]

### Governance and policies

- Our [Code of Conduct]

### Commercial support

Thinking about using {{product}} for your next project? [Get in touch!]

<!-- IMAGES -->

[logo]: https://assets.ubuntu.com/v1/843c77b6-juju-at-a-glace.svg

<!-- LINKS -->

[Code of Conduct]: https://ubuntu.com/community/ethos/code-of-conduct
[community]: /community
[contribute]: /charm/howto/contribute
[releases]: /releases/charm/index
[what is Canonical Kubernetes page]: /about
[arch]: /charm/explanation/architecture
[Juju]: https://juju.is
[k8s snap package]: /snap/index
[Diátaxis framework]: https://diataxis.fr/
[Canonical Kubernetes Slack]: https://kubernetes.slack.com/archives/CG1V2CAMB
[Canonical Kubernetes Discourse]: https://discourse.ubuntu.com/c/kubernetes/180
[Get in touch!]: https://ubuntu.com/kubernetes/contact-us
