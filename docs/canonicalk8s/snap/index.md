---
myst:
  html_meta:
    description: "Explore the official Canonical Kubernetes snap documentation. Includes step-by-step tutorials, practical how-to guides, in-depth explanations, and technical reference."
---

# {{product}} snap documentation

```{toctree}
:hidden:
Overview <self>
```

```{toctree}
:hidden:
:titlesonly:
:maxdepth: 6
tutorial/index.md
howto/index.md
explanation/index.md
reference/index.md
```

The {{product}} snap is a performant, lightweight, secure and
opinionated distribution of **Kubernetes** which includes everything needed to
create and manage a scalable cluster suitable for all use cases.

You can find out more about {{product}} on the 
[what is Canonical Kubernetes page] or see a more detailed explanation in our
[architecture documentation].

For deployment at scale, {{product}} is also available as a
[Juju charm][]

<!-- ## In this documentation  -->

<!-- All docs currently  -->

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( tutorial/getting-started) • [What is Canonical Kubernetes?](about)|
| **Deployment** | [`k8s` snap install](howto/install/snap) • [Air-gapped environments install](howto/install/offline) • [Development environments install](howto/install/dev-env) • [Custom bootstrap config install](howto/install/custom-bootstrap-config) • [Custom worker config install](howto/install/custom-worker) • [Multipass VMs](howto/install/multipass) • [LXD VMs](howto/install/lxd.md) • [Uninstall](howto/install/uninstall)|
| **Networking** |  [Overview](explanation/networking) • [Configure default networking features](howto/networking/index.md) • [Install a firewall](howto/networking/ufw) • [Enable dual stack](howto/networking/dualstack) • [Deploy IPv6 only clusters](howto/networking/ipv6) • [Ports and services](reference/ports-and-services) • [Proxy environment variables](reference/proxy.md) |
| **Security and compliance** |  [Explanation](explanation/security.md) • [Harden your cluster](howto/security/hardening)  • [Report an issue](howto/security/report-security-issue.md) •  [Refresh Kubernetes certs](howto/security/refresh-certs) • [Refresh external certs](howto/security/refresh-external-certs) • [Vault intermediate CA](howto/security/intermediate-ca) • [DISA STIG](howto/install/disa-stig) • [FIPS](howto/install/fips) • [CIS](howto/security/cis-assessment)|
| **Storage** |  [Use default storage](howto/storage/storage) • [Deploy Ceph](howto/storage/ceph) • [Cluster datastore](reference/dqlite.md) • [External datastore](howto/external-datastore)  |
| **Cluster management** | [Understanding upgrades](explanation/upgrade) • [Managing upgrades](howto/upgrades) • [Node roles](explanation/roles) • [High availablity](explanation/high-availability) • [Clustering](explanation/clustering) • [Choose a channel](explanation/channels) • [Helm](explanation/package-management) • [Image management](howto/image-management) • [Architecture](explanation/architecture)|
| **Troubleshooting** | [Troubleshoot your cluster](howto/troubleshooting) • [Get support](howto/support) |
| **Observability** | [Deploy COS](howto/observability) |
| **Disaster recovery** | [Recover after quorum loss](howto/restore-quorum) • [Inspection reports](reference/inspection-reports) • [Back and restore](howto/backup-restore)|
| **Hardware enablement** |  [EPA explanation](explanation/epa) • [Enhanced Platform Awareness setup](howto/epa) |
| **Configuration** | [Annotations](reference/annotations.md)  • [Commands](reference/commands.md) • [Config files](reference/config-files/index) |


## In this documentation 

<!-- Core features  -->
<!--  -->
|                                                                     |                                                                     |
|---------------------------------------------------------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( tutorial/getting-started) • [What is Canonical Kubernetes?](about)|
| **Deployment** | [`k8s` snap install](howto/install/snap) • [Air-gapped environments install](howto/install/offline) • [Development environments install](howto/install/dev-env) • [Custom bootstrap config install](howto/install/custom-bootstrap-config) • [Custom worker config install](howto/install/custom-worker) • [Multipass VMs](howto/install/multipass) • [LXD VMs](howto/install/lxd.md) • [Uninstall](howto/install/uninstall)|
| **Networking** |  [Overview](explanation/networking) • [Configure default networking features](howto/networking/index.md) • [Install a firewall](howto/networking/ufw) • [Enable dual stack](howto/networking/dualstack) • [Deploy IPv6 only clusters](howto/networking/ipv6) • [Ports and services](reference/ports-and-services) • [Proxy environment variables](reference/proxy.md) |
| **Security and compliance** |  [Explanation](explanation/security.md) • [Harden your cluster](howto/security/hardening)  • [Report an issue](howto/security/report-security-issue.md) •  [Refresh Kubernetes certs](howto/security/refresh-certs) • [Refresh external certs](howto/security/refresh-external-certs) • [DISA STIG](howto/install/disa-stig) • [FIPS](howto/install/fips) • [CIS](howto/security/cis-assessment)|
| **Storage** |  [Use default storage](howto/storage/storage) • [Cluster datastore](reference/dqlite.md) |
| **Cluster management** | [Understanding upgrades](explanation/upgrade) • [Managing upgrades](howto/upgrades) • [Node roles](explanation/roles) • [High availablity](explanation/high-availability) • [Clustering](explanation/clustering) • [Choose a channel](explanation/channels) • [Architecture](explanation/architecture)|
| **Troubleshooting** | [Troubleshoot your cluster](howto/troubleshooting) • [Get support](howto/support) |
| **Disaster recovery** | [Recover after quorum loss](howto/restore-quorum) • [Inspection reports](reference/inspection-reports) |
| **Configuration** | [Annotations](reference/annotations.md)  • [Commands](reference/commands.md) • [Config files](reference/config-files/index) |

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
[contribute]: /snap/howto/contribute
[releases]: /releases/snap/index
[what is Canonical Kubernetes page]: /about
[architecture documentation]: /snap/explanation/architecture
[Juju charm]: /charm/index
[Diátaxis framework]: https://diataxis.fr/
[Canonical Kubernetes Slack]: https://kubernetes.slack.com/archives/CG1V2CAMB
[Canonical Kubernetes Discourse]: https://discourse.ubuntu.com/c/kubernetes/180
[Get in touch!]: https://ubuntu.com/kubernetes/contact-us
