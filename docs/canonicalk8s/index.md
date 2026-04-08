---
myst:
  html_meta:
    description: "Official Canonical Kubernetes documentation. Learn to deploy and manage lightweight, secure clusters on Ubuntu. Includes tutorials, how-to guides, explanation and reference docs."
---

# {{product}} documentation

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

## In this documentation 

`````{tab-set}
````{tab-item} Snap
|                                                                     |                                                                     |
|---------------------------------------------------------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( tutorial/getting-started) • [What is Canonical Kubernetes?](/about)|
| **Deployment** | [`k8s` snap install](howto/install/snap) • [Air-gapped environments install](howto/install/offline) • [Development environments install](howto/install/dev-env) • [Custom bootstrap config install](howto/install/custom-bootstrap-config) • [Custom worker config install](howto/install/custom-worker) • [Multipass VMs](howto/install/multipass) • [LXD VMs](howto/install/lxd.md) • [Uninstall](howto/install/uninstall)|
| **Networking** |  [Overview](explanation/networking) • [Configure default networking features](howto/networking/index.md) • [Install a firewall](howto/networking/ufw) • [Enable dual stack](howto/networking/dualstack) • [Deploy IPv6 only clusters](howto/networking/ipv6) • [Ports and services](reference/ports-and-services) • [Proxy environment variables](reference/proxy.md) |
| **Security and compliance** |  [Explanation](explanation/security.md) • [Harden your cluster](howto/security/hardening)  • [Report an issue](howto/security/report-security-issue.md) •  [Refresh Kubernetes certs](howto/security/refresh-certs) • [Refresh external certs](howto/security/refresh-external-certs) • [DISA STIG](howto/install/disa-stig) • [FIPS](howto/install/fips) • [CIS](howto/security/cis-assessment)|
| **Storage** |  [Use default storage](howto/storage/storage) • [Cluster datastore](reference/dqlite.md) |
| **Cluster management** | [Understanding upgrades](explanation/upgrade) • [Managing upgrades](howto/upgrades) • [Node roles](explanation/roles) • [High availablity](explanation/high-availability) • [Clustering](explanation/clustering) • [Choose a channel](explanation/channels) • [Architecture](explanation/architecture)|
| **Troubleshooting** | [Troubleshoot your cluster](howto/troubleshooting) • [Get support](howto/support) |
| **Disaster recovery** | [Recover after quorum loss](howto/restore-quorum) • [Inspection reports](reference/inspection-reports) |
| **Configuration** | [Annotations](reference/annotations.md)  • [Commands](reference/commands.md) • [Config files](reference/config-files/index) |

````
````{tab-item} Charm
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
````
````{tab-item} CAPI
|                                                                     |                                                                     |
|---------------------------------------------------------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( tutorial/getting-started) • [What is Canonical Kubernetes?](/about)|
| **Deployment** | [Provision a cluster](howto/provision) • [Custom bootstrap config install](howto/custom-bootstrap-config) • [Custom k8s version install](howto/custom-ck8s) |
| **Networking** |  [Overview](explanation/networking) • [Ports and services](reference/ports-and-services) |
| **Security and compliance** |  [Explanation](explanation/security)  • [Refresh external certs](howto/refresh-certs) |
| **Cluster management** | [Understanding upgrades](explanation/in-place-upgrade) • [Manage in place upgrades](howto/in-place-upgrades) • [Rollout upgrades](howto/rollout-upgrades) • [Clustering](explanation/clustering) • [Migrate the cluster](howto/migrate-management)|
| **Troubleshooting** | [Troubleshoot your cluster](howto/troubleshooting) |
| **Configuration** | [Annotations](reference/annotations.md)  • [Config files](reference/configs) |
````
`````

## How this documentation is organized
<!-- markdownlint-disable -->
{{product}} can be deployed and managed as a standalone snap, as a charm as part of a
Juju cluster or with Cluster API. Find out more about which {{product}}
deployment method is best for your
project's needs with
**[choosing a {{product}} installation method.](/snap/explanation/installation-methods.md)**
<!-- markdownlint-restore -->

```{toctree}
:hidden:
:titlesonly:
Canonical Kubernetes documentation <self>
```

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

````{grid} 3

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

````

## In this documentation


### Getting started 

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Getting started** | [Tutorial]( snap/tutorial/getting-started) • [What is Canonical Kubernetes?](about) • [Snap, charm or CAPI?](snap/explanation/installation-methods)|

### Core Kubernetes features

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Deployment** | [`k8s` snap install options](snap/howto/install/index) • [`k8s` charms install options](charm/howto/install/index) • [Provision with Cluster API](capi/howto/provision.md)|
| **Networking** | [Networking overview](snap/explanation/networking) • [Configure default networking features](snap/howto/networking/index) • [Enable dual stack](snap/howto/networking/dualstack) • [Deploy IPv6 only cluster](snap/howto/networking/ipv6) • [Ports and services](snap/reference/ports-and-services) • [Proxy environment variables](snap/reference/proxy.md) | • |
| **Storage** | [Use default storage](snap/howto/storage/storage) • [Cluster datastore](reference/dqlite.md) |
| **Security** | [Security overview](snap/explanation/security) • [Cluster hardening](snap/howto/security/hardening) • [Report and issue](snap/howto/security/report-security-issue) |
| **Cluster management** | [Upgrade your cluster](snap/howto/upgrades) • [Understand upgrades](snap/explanation/upgrade) • [Node roles](snap/explanation/roles) • [High availability](snap/explanation/high-availability) • [Clustering](snap/explanation/clustering.md) • [Choose a channel](snap/explanation/channels) • [Architecture](snap/explanation/architecture) |
| **Troubleshooting** | [Troubleshoot your cluster](snap/howto/troubleshooting) • [Get support](snap/reference/inspection-reports) |
| **Disaster recovery** | [Recover after quorum loss](snap/howto/restore-quorum) • [Inspection report](snap/reference/inspection-reports) |

### k8s snap

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Security compliance** | [DISA STIG](snap/howto/install/disa-stig) • [FIPS](snap/howto/install/fips) • [CIS](snap/howto/security/cis-assessment) | 
| **Configuration** | [Annotations](snap/reference/annotations) • [Commands](snap/reference/commands) • [Configuration files](snap/reference/config-files/index)   | 

### k8s charms 

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Charm integrations** | [Openstack](charm/howto/openstack) • [etcd](charm/howto/etcd) • [Ceph CSI](charm/howto/ceph-csi) • [COS Lite](charm/howto/cos-lite.md) |
| **Configuration** | [Configure the cluster](charm/howto/configure-cluster) • [Configuration options](charm/reference/charm-configurations)• [Actions](charm/reference/actions) • [Charmhub links](charm/reference/charms) • [Availability zones](charm/reference/az)| 

### Cluster API

|                    |                                                                     |
|--------------------|---------------------------------------------------------------------|
| **Cluster lifecycle** | [CAPI and Canonical Kubernetes](capi/explanation/capi-k8s) • [In place upgrades explanation](capi/explanation/in-place-upgrades)|
| **Configuration** | [Annotations](reference/annotations.md)  • [Config files](reference/configs) |



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
