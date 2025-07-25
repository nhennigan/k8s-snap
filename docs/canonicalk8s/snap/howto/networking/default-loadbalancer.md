# How to use the default load balancer

{{product}} includes a default load balancer. As this is not an
essential service for all deployments, it is not enabled by default. This guide
explains how to configure and enable the `load-balancer`.

## Prerequisites

This guide assumes the following:

- You have root or sudo access to the machine.
- You have a bootstrapped {{product}} cluster (see the [Getting
  Started][getting-started-guide] guide).

## Check the status and configuration

Find out whether load balancer is enabled or disabled with the following
command:

```
sudo k8s status
```

The load balancer is not enabled by default, it won't be listed on the status
output unless it has been subsequently enabled.

To check the current configuration of the `load-balancer`, run the following:

```
sudo k8s get load-balancer
```

This should output a list of values like this:

- `enabled`: if set to true, load-balancer is enabled
- `cidrs` - a list containing [CIDR] or IP address ranges for the
load balancer's address pool
- `l2-mode` - whether L2 mode (failover) is turned on
- `l2-interfaces` - optional list of interfaces to announce services over
  (defaults to all)
- `bgp-mode` - whether BGP mode is active.
- `bgp-local-asn` - the local Autonomous System Number (ASN)
- `bgp-peer-address` - the peer address
- `bgp-peer-asn` - ASN of the peer network
- `bgp-peer-port` - port used on the BGP peer

These values are configured using the `k8s set` command, e.g.:

```
sudo k8s set load-balancer.l2-mode=true
```

Note that for the BGP mode, it is necessary to set ***all*** the values
simultaneously. E.g.

```
sudo k8s set load-balancer.bgp-mode=true load-balancer.bgp-local-asn=64512 load-balancer.bgp-peer-address=10.0.10.63 load-balancer.bgp-peer-asn=64512 load-balancer.bgp-peer-port=7012
```

## Enable the load balancer

To enable the load balancer, run:

```
sudo k8s enable load-balancer
```

You can now confirm it is working by running:

```
sudo k8s status
```

```{important}
If you run `k8s status` soon after enabling the load balancer in BGP mode,
`k8s status` might report errors. Please wait a few moments for the load balancer to finish deploying and try again.
```

## Disable the load balancer

The default load balancer can be disabled again with:

```
sudo k8s disable load-balancer
```

## Next Step

- Learn more in the [Load-Balancer] explanation page.

<!-- LINKS -->
[CIDR]: https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
[getting-started-guide]: ../../tutorial/getting-started
[Load-Balancer]: ../../explanation/load-balance-workloads.md
