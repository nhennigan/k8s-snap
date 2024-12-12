# {{product}} tutorials

```{toctree}
:hidden:
Overview <self>
```

```{toctree}
:hidden:
:titlesonly:
:maxdepth: 6
snap/index.md
charm/index.md
capi/index.md
```

The {{product}} snap is a performant, lightweight, secure and
opinionated distribution of **Kubernetes** which includes everything needed to
create and manage a scalable cluster suitable for all use cases.

You can find out more about {{product}} on this [overview page] or
see a more detailed explanation in our [architecture documentation].

For deployment at scale, {{product}} is also available as a
[Juju charm][]

![Illustration depicting working on components and clouds][logo]

---

## In this documentation

````{grid} 1 1 2 2

```{grid-item-card} [Snap Tutorials](snap/index)
[Install](snap/getting-started.md )

[Add and remove nodes](snap/add-remove-nodes.md )

[Learn basic kubectlcommands](snap/kubectl.md)

```

```{grid-item-card} [Charm Tutorials](charm/index)

[Install](charm/getting-started.md)
```

````

````{grid} 1 1 2 2


```{grid-item-card} [CAPI Tutorials](capi/index)
[Install](capi/getting-started.md)
```

```{grid-item-card} 

```

````

---

## Project and community

{{product}} is a member of the Ubuntu family. It's an open source
project which welcomes community involvement, contributions, suggestions, fixes
and constructive feedback.

- Our [Code of Conduct]
- Our [community]
- How to [contribute]
- Our [release notes][releases]

<!-- IMAGES -->

[logo]: https://assets.ubuntu.com/v1/843c77b6-juju-at-a-glace.svg

<!-- LINKS -->

[Code of Conduct]: https://ubuntu.com/community/ethos/code-of-conduct
[community]: ./reference/community
[contribute]: ./howto/contribute
[releases]: ./reference/releases
[overview page]: ./explanation/about
[architecture documentation]: ./reference/architecture
[Juju charm]: ../charm/index
