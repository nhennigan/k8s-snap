# Monthly Patch Notice Review

## Included

> Edit summaries freely. Keep the `<!-- sha:... -->` tags — `finalize` uses them to update state.

<!-- sha:d45056ad2e0587c2aaec6c45dfa969fa28bee309 -->
<!-- sha:4ba3f8e87f30a3d42666c63fd8a076dce5bea1ea -->
- **Major Feature** Add ServiceArgsController to automatically detect and remediate service argument drift, improving operational consistency.
  _(Group: ServiceArgsController — covers: `d45056ad` feat: add ServiceArgsController to manage service argument drift and restart services, `4ba3f8e8` fix: enhance WatchConfigMap to seed existing ConfigMap and handle errors)_

<!-- sha:593219de7bd221340e6c2e6a9c53cc1ad6c84c0d -->
- **Security** Resolves two Go dependency vulnerabilities including a critical gRPC CVE (CVE-2026-33186) and a medium-severity xz CVE (CVE-2025-58058).

<!-- sha:50899e6e9b98aa7b97d5778d3a4a3b7b050d7de9 -->
- **Bug Fix** Prevent etcd quorum loss when joining a second control-plane node by using learner mode with safe retry-based promotion.

<!-- sha:bbf4e215b40e24090db308fb37fcc45943f203bd -->
- **Bug Fix** Improve cluster readiness detection by verifying CoreDNS has a cluster IP assigned before reporting the cluster as ready.

<!-- sha:b72fd2ba5061852729754bdf861911951f3a00ee -->
- **Bug Fix** Fixes k8sconfig watch resumption after etcd compaction, preventing missed configuration updates on long-running clusters.

<!-- sha:5382c9d68716f9d67405596a2998981fdbf1653e -->
<!-- sha:8a03f963600993e4e8957993f5e86fb5170c8c9d -->
- **Component Bump** Updates packaged component versions including MetalLB v0.15.3-ck2 and Helm to v4.1.4
  _(Group: Component bumps — covers: `5382c9d6` [release-1.35] Update component versions (#2523), `8a03f963` feat: bump metallb rock to v0.15.3-ck2 (#2561))_


## Verification

> Cross-check summaries against original commit titles.

- [`d45056ad`](https://github.com/canonical/k8s-snap/commit/d45056ad2e0587c2aaec6c45dfa969fa28bee309) — feat: add ServiceArgsController to manage service argument drift and restart services
- [`4ba3f8e8`](https://github.com/canonical/k8s-snap/commit/4ba3f8e87f30a3d42666c63fd8a076dce5bea1ea) — fix: enhance WatchConfigMap to seed existing ConfigMap and handle errors
- [`593219de`](https://github.com/canonical/k8s-snap/pull/2484) (PR #2484) — fix(deps): bump vulnerable Go dependencies (#2484)
- [`5885966c`](https://github.com/canonical/k8s-snap/pull/2552) (PR #2552) — docs: Add patch notices to our release notes (#2547) (#2552)
- [`50899e6e`](https://github.com/canonical/k8s-snap/pull/2512) (PR #2512) — fix: use etcd learner mode during node join to prevent quorum loss (1.35) (#2512)
- [`bbf4e215`](https://github.com/canonical/k8s-snap/commit/bbf4e215b40e24090db308fb37fcc45943f203bd) — feat: enhance getClusterStatus to check CoreDNS service cluster IP for readiness
- [`b72fd2ba`](https://github.com/canonical/k8s-snap/pull/2578) (PR #2578) — fix: watching k8sconfig resource after compaction (#2578)
- [`5382c9d6`](https://github.com/canonical/k8s-snap/pull/2523) (PR #2523) — [release-1.35] Update component versions (#2523)
- [`8a03f963`](https://github.com/canonical/k8s-snap/pull/2561) (PR #2561) — feat: bump metallb rock to v0.15.3-ck2 (#2561)
- [`86f0016e`](https://github.com/canonical/k8s-snap/pull/2570) (PR #2570) — docs: change CA rotation warning to reflect upstream state [Backport release-1.35] (#2570)

## Discarded

> Items the AI considers noise. Move to Included (with a sha tag) if you disagree.

- `ea2d0da3` PR #2502 — docs: fix broken privileged container link in LXD install guide (#2487) (#2502) | _Minor documentation fix (broken link) with no change to operator workflow or supported procedure._
- `297997cf` PR #2504 — ci: pin all GitHub Actions dependencies to SHA hashes (#2491) (#2504) | _CI-only change pinning GitHub Actions to SHA hashes; no impact on shipped behaviour._
- `deeec124` PR #2518 — ci: remove stale src/k8s/go.mod reference from update scripts (#2518) | _CI maintenance removing a stale file reference from internal update scripts._
- `a9aced83` PR #2525 — test: increase feature controller test retry window [release-1.35] (#2525) | _Test-only change increasing retry window in the feature controller chaos test._
- `24c7b3a6` — fix: update log context in NodeLabelController to reflect correct controller name | _Internal logging fix correcting controller name in log context; no user-facing behaviour change._
- `8cb3a1fc` PR #2536 — test(dns): add regression test for CoreDNS propagation to late-joined nodes (#2536) | _Test-only addition; the underlying fix is captured by the included CoreDNS readiness commit._
