---
myst:
  html_meta:
    description: "Official Canonical Kubernetes documentation. Learn to deploy and manage lightweight, secure clusters on Ubuntu. Includes tutorials, how-to guides, explanation and reference docs."
---
# {{product}} documentation

```{toctree}
:hidden:
:titlesonly:
:maxdepth: 6
about.md
Deploy from Snap package </snap/index.md>
Deploy with Juju </charm/index.md>
Deploy with Cluster API </capi/index.md>
Community </community.md>
Release notes </releases/index.md>
```

```{toctree}
:hidden:
:titlesonly:
:maxdepth: 6
about.md
Tutorial </tutorial/getting-started.md>
How-to guides </howto/index.md>
Explanation </explanation/index.md>
Reference </reference/index.md>
Community </community.md>
Release notes </releases/index.md>
```

{{product}} is a performant, lightweight, secure and
opinionated distribution of **Kubernetes** which includes everything needed to
create and manage a scalable cluster suitable for all use cases.

{{product}} builds upon upstream Kubernetes by providing all the extra services
such as a container runtime, a CNI, DNS services, an ingress gateway and more
that are necessary to have a fully functioning cluster all in one convenient
location - a snap!

Staying up-to-date with upstream Kubernetes security
patches and updates with {{product}} is a seamless experience, freeing up time
for application
development and innovation without having to worry about the infrastructure.

Whether you are deploying a small cluster to get accustomed to Kubernetes or a
huge enterprise level deployment across the globe, {{product}} can cater to
your needs. If you would like to jump straight in, head to the
[snap getting started tutorial!](/snap/tutorial/getting-started.md)

![Illustration depicting working on components and clouds][logo]

---

## In this documentation

### Getting started 

Canonical Kubernetes: [Tutorial](./tutorial/getting-started.md) • [What is Canonical Kubernetes?](./about.md) • [Snap, charm or CAPI?](./explanation/installation-methods.md)

### Deployment 

Snap: [k8s snap](./howto/install/snap.md) • [Custom bootstrap config](./howto/install/custom-bootstrap-config.md) • [Add a worker](./howto/install/custom-worker.md) • [Development environment](./howto/install/dev-env.md) • [Multipass](./howto/install/multipass.md) • [LXD](./howto/install/lxd.md)

Charm: [k8s charm](./howto/install/charm.md) • [Custom bootstrap config](./howto/install/custom-bootstrap-config.md) • [Add a worker](./howto/install/custom-workers.md) • [LXD](./howto/install/lxd.md) • [Terraform](./howto/install/install-terraform.md)

CAPI: [k8s CAPI](./howto/install/provision.md) • [Custom bootstrap config](./howto/install/custom-bootstrap-config.md) • [Custom Kubernetes version](./howto/install/custom-ck8s.md)

### Core features and architecture 

**Networking**: [Overview](./explanation/networking.md) • [DNS](./howto/networking/default-dns.md) • [Network](./howto/networking/default-network.md) • [Load balancer](./howto/networking/default-loadbalancer.md) • [Ingress](./howto/networking/default-ingress.md) • [Gateway](./howto/networking/default-gateway.md) • [Dual stack](./howto/networking/dualstack.md) • [IPv6 only](./howto/networking/ipv6.md) • [Port and services](./reference/ports-and-services.md)

**Proxy networking**: [Configure proxy](./howto/networking/proxy.md) • [Proxy environment variables](./reference/proxy.md)

**Storage**: [Use default storage](./howto/storage/storage.md) • [etcd](./reference/etcd.md) • [Dqlite](./reference/dqlite.md) • [Use an external datastore](./howto/storage/external-datastore.md) • [Backup and restore]()

**Monitoring**: [Observability]()

**Scaling**: [High availability](./explanation/high-availability.md) • [Clustering](./explanation/clustering.md) • [Node role](./explanation/roles.md)

**Configuration**: Configuration files • Annotations • Commands • Availability zones •  Actions • Providers configs 

**Architectural**: [Architecture overview](./explanation/architecture.md)	 • [Cluster API and Canonical Kubernetes](./explanation/capi-ck8s.md) 

### External integrations 

**Charm integrations**: [OpenStack](./howto/charm/openstack.md) • [etcd](./howto/charm/etcd.md) • [Ceph-CSI](./howto/charm/ceph-csi.md) • [COS Lite ](./howto/charm/cos-lite.md)


### Security 

**Security**: About   • Cluster hardening  • Refresh certificates • Air-gapped deployments • Configure firewall • Cluster certificates 

**Compliance**: [DISA STIG]() • [CIS]() • [FIPS]()

### Lifecycle management 

**Installation**: [Package management with Helm](./explanation/package-management.md)  •  [Choose a channel](./explanation/channels.md)

**Troubleshooting**:  [Troubleshoot your cluster](./howto/) •  Get support

**Disaster recovery**:  [Recover after quorum loss](./howto/) • [Inspection reports](./reference/inspection-reports.md)

**Upgrades**: [Explanation](./explanation/upgrade.md) • [Manage upgrades]() •  [In place upgrades]() 

**Images**: [Manage images](./howto/)
 
**Migration**: [Migrate CAPI cluster](./howto/)


<!-- ````{grid} 3

```{grid-item-card}
:link: snap/
### [Canonical Kubernetes snap ›](/snap/index)

The `k8s` snap is a self-contained, secure and dependency-free Linux app package used to deploy and manage a {{product}} cluster. If you are new to Kubernetes, start here.
```

```{grid-item-card}
:link: charm/
### [Canonical Kubernetes charms ›](/charm/index)

The `k8s` charms take care of installing, configuring and managing {{product}} on cloud instances managed by Juju.
```

```{grid-item-card}
:link: capi/
### [Canonical Kubernetes and Cluster API ›](/capi/index)

Using Cluster API's declarative tooling, deploy and manage multiple {{product}} clusters.
```

```` -->

## How this documenation is organised 

- The [Tutorial](./tutorial/getting-started.md) takes you step-by-step through deploying your first Canonical Kubernetes cluster.
- [How-to guides](./howto/index.md) provide directions covering key cluster operations and common tasks.
- [Reference](./reference/index.md) contains technical definitions of APIs, configuration and internal components.
- [Explanation](./explanation/index.md) includes topic overviews, background and context and detailed discussion.

---

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
[releases]: /releases/index
[Canonical Kubernetes Slack]: https://kubernetes.slack.com/archives/CG1V2CAMB
[Canonical Kubernetes Discourse]: https://discourse.ubuntu.com/c/kubernetes/180
[Get in touch!]: https://ubuntu.com/kubernetes/contact-us
