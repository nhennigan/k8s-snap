# Contribute to {{product}} documentation    

Our aim is to provide easy-to-understand documentation on all aspects of
{{product}}, so we greatly appreciate your feedback and contributions.
See our [community page][] for ways of getting in touch.

The source of the documentation and the system used to build it are included in
the [main repository for the {{product}} snap][code repo].

### Documentation framework

This documentation has adopted the Diátaxis framework. You can read more about
it on the [Diátaxis website]. In essence though, this guides the way we
categorize and write our documentation. You can see there are four main
categories of documentation:

- **Tutorials** for guided walk-throughs
- **How to** pages for specific tasks and goals
- **Explanation** pages which give background reasons and, well, explanations
- **Reference**, where you will find the commands, the roadmap, etc.

Every page of documentation should fit into one of those categories. If it
doesn't you may consider if it is actually two pages (e.g. a How to *and* an
explanation).

We have included some tips and outlines of the different types of docs we
create to help you get started:

- [Tutorial template][]
- [How to template][]
- [Explanation template][]
- [Reference template][]

### Small changes

If you are simply correcting a typo or updating a link, you can follow the
'Contribute to this page' link (the pencil icon) on any page and it will take 
you to the online GitHub editor to make your change. You will still need to 
raise a pull request and explain your change to get it reviewed.

### Myst, Markdown and Sphinx

We use Canonical's [Sphinx-based starter pack] to build the documentation which
is then hosted on ReadtheDocs. The documentation source files are kept inside 
the k8s snap source code in the `docs/canonicalk8s` directory.

Although Sphinx is normally associated with the `ReSTructured text` format, we
write all our documentation in Markdown to make it easier for humans to work
with. There are a few extra things that come with this - certain features need
to be specially marked up (e.g. admonitions) to be processed properly. There is
a guide to using `Myst` (which is a Markdown extension for Sphinx) directives
and formatting available at [Canonical starter pack documentation].

### Local testing

To test your changes locally, you can build a local version of the
documentation. Open a terminal and go to the `/docs/canonicalk8s` directory. 
From there you can run the command:

```
make run
```

This will create a local environment, install all the dependencies and build
the docs. The output will then be served locally - check the output for the
URL. Using the `run` option means that the docs will automatically be
regenerated when you change any of the source files too (though remember to
press `F5` in your browser to reload the page without caching)!

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

<!-- LINKS -->

[code repo]: https://github.com/canonical/k8s-snap
[Diátaxis website]: https://diataxis.fr/
[_parts]: https://github.com/canonical/k8s-snap/blob/main/docs/canonicalk8s/_parts/doc-cheat-sheet-myst.md
[community page]: /community
[Tutorial template]: https://raw.githubusercontent.com/canonical/k8s-snap/main/docs/canonicalk8s/_templates/template-tutorial
[How to template]: https://raw.githubusercontent.com/canonical/k8s-snap/main/docs/canonicalk8s/_templates/template-howto
[Explanation template]: https://raw.githubusercontent.com/canonical/k8s-snap/main/docs/canonicalk8s/_templates/template-explanation
[Reference template]: https://raw.githubusercontent.com/canonical/k8s-snap/main/docs/canonicalk8s/_templates/template-reference
[development env guide]: install/dev-env.md
[Canonical starter pack documentation]: https://canonical-starter-pack.readthedocs-hosted.com/stable/reference/myst-syntax-reference
[Sphinx-based starter pack]: https://github.com/canonical/sphinx-docs-starter-pack 
