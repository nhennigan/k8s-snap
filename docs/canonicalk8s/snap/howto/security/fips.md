# WIP - FIPS

## Enable FIPS on kernel

ubuntu pro subscription attach

enable FIPS

```
sudo pro enable fips-updates
```

## Deploy K8s with FIPS

```
sudo snap install k8s --classic --channel=1.33-classic/stable
```

extra FIPS steps

Make sure that nodes are joined with their default hostname to comply with V-242404

## Hardening guide

### Control plane nodes

<!-- #### Encrypt secrets at rest

Encrypt key-value store secrets rather than leaving it as base64 encoded values
as described in the upstream Kubernetes documentation on
[encrypting secrets][encryption_at_rest].

Create the `EncryptionConfiguration` file under `/var/snap/k8s/common/etc/encryption/`.

SHOULD WE PROMPT THAT YOU SHOULD INCLUDE YOUR OWN KEY HERE AND THAT IS WHY WE HAVE NOT INCLUDED IT?

```
sudo sh -c '
mkdir -p /var/snap/k8s/common/etc/encryption/
cat >/var/snap/k8s/common/etc/encryption/enc.yaml << EOL
kind: "EncryptionConfig"
apiVersion: apiserver.config.k8s.io/v1
resources:
- resources: ["secrets"]
  providers:
  - aesgcm:
      keys:
      - name: key1
        secret: ${BASE 64 ENCODED SECRET}
  - identity: {}
EOL
chmod 600 /var/snap/k8s/common/etc/encryption/enc.yaml
```


mkdir -p /var/snap/k8s/common/etc/encryption/
sudo cat <<EOF > /var/snap/k8s/common/etc/encryption/enc.yaml
kind: "EncryptionConfig"
apiVersion: apiserver.config.k8s.io/v1
resources:
- resources: ["secrets"]
  providers:
  - aesgcm:
      keys:
      - name: key1
        secret: ${BASE 64 ENCODED SECRET}
  - identity: {}
EOF
sudo chmod 600 /var/snap/k8s/common/etc/encryption/enc.yaml


Set the `--encryption-provider-config` file as an argument to the kubernetes
apiserver.

```
sudo sh -c '
cat >>/var/snap/k8s/common/args/kube-apiserver <<EOL
--encryption-provider-config=/var/snap/k8s/common/etc/enc.yaml
EOL'
```

Securing the contents of this key file is left as a separate exercise.

WE ALREADY HAVE RBAC BY DEFAULT. DO WE RECOMMEND ANY OTHER RBAC?

#### Configure authorization modes
Enforce RBAC (Role-Based Access Control) policies and confirm the value of the
apiserver [`authorization-mode`][authorization_mode]:
* includes `RBAC`
* doesn't include `AlwaysAllow`

```
sudo grep authorization-mode /var/snap/k8s/common/args/kube-apiserver | \
    grep -q "RBAC" && echo "okay" || echo "missing"
sudo grep authorization-mode /var/snap/k8s/common/args/kube-apiserver | \
    grep -q "AlwaysAllow" && echo "Remove AlwaysAllow" || echo "okay"
```

By default, the value is `Node,RBAC`
* `Node`:
  A special-purpose authorization mode that grants permissions
  to kubelets based on the pods they are scheduled to run.

 To apply RBAC to other cluster resources, see the upstream Kubernetes
 [RBAC guide][access_authn_authz]. -->


#### Configure log auditing

<!-- DO WE HAVE A RECOMMENDED LEVEL OR IS THIS ON THE USER -->

<!-- ADDRESSES V-242402, V-242403, V-242461, V-242462, V-242463, V-242464, V-242465 -->
```{note}
Configuring log auditing requires the cluster administrator's input and
may incur performance penalties in the form of disk I/O.
```

Create an audit-policy.yaml file under `/var/snap/k8s/common/etc/` and specify
the level of auditing you desire based on the [upstream instructions].
Here is a minimal example of such a policy file.

```
sudo mkdir -p /var/snap/k8s/common/etc/
sudo sh -c 'cat >/var/snap/k8s/common/etc/audit-policy.yaml <<EOL
# Log all requests at the Metadata level.
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
EOL'
```

Enable auditing at the API server level by adding the following arguments.

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kube-apiserver <<EOL
--audit-log-path=/var/log/kubernetes/audit.log
--audit-log-maxage=30
--audit-log-maxbackup=10
--audit-log-maxsize=100
--audit-policy-file=/var/snap/k8s/common/etc/audit-policy.yaml
EOL'
```

Restart the API server:

```
sudo systemctl restart snap.k8s.kube-apiserver
```

#### Set event rate limits

```{note}
Configuring event rate limits requires the cluster administrator's input
in assessing the hardware and workload specifications/requirements.
```


Create a configuration file with the [rate limits] and place it under
`/var/snap/k8s/common/etc/`.
For example:

```
sudo mkdir -p /var/snap/k8s/common/etc/
sudo sh -c 'cat >/var/snap/k8s/common/etc/eventconfig.yaml <<EOL
apiVersion: eventratelimit.admission.k8s.io/v1alpha1
kind: Configuration
limits:
  - type: Server
    qps: 5000
    burst: 20000
EOL'
```

Create an admissions control config file under `/var/k8s/snap/common/etc/` .

```
sudo mkdir -p /var/snap/k8s/common/etc/
sudo sh -c 'cat >/var/snap/k8s/common/etc/admission-control-config-file.yaml <<EOL
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
  - name: EventRateLimit
    path: eventconfig.yaml
EOL'
```

Make sure the EventRateLimit admission plugin is loaded in the
`/var/snap/k8s/common/args/kube-apiserver` .

```
--enable-admission-plugins=...,EventRateLimit,...
```

Load the admission control config file.

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kube-apiserver <<EOL
--admission-control-config-file=/var/snap/k8s/common/etc/admission-control-config-file.yaml
EOL'
```

Restart the API server.

```
sudo systemctl restart snap.k8s.kube-apiserver
```

<!-- DOES NOT SEEM TO CORRELATE TO DISA STIG -->
#### Enable AlwaysPullImages admission control plugin

```{note}
Configuring the AlwaysPullImages admission control plugin may have performance
impact in the form of increased network traffic and may hamper offline deployments
that use image sideloading.
```

Make sure the AlwaysPullImages admission plugin is loaded in the
`/var/snap/k8s/common/args/kube-apiserver`

```
--enable-admission-plugins=...,AlwaysPullImages,...
```

Restart the API server.

```
sudo systemctl restart snap.k8s.kube-apiserver
```


#### Set the Kubernetes scheduler and controller manager bind address

<!-- WHAT WORKLOADS? -->

<!-- ADDRESSES V-242384, V-242385 -->
```{note}
This configuration may affect compatibility with workloads and metrics
collection.
```

Edit the Kubernetes scheduler arguments file
`/var/snap/k8s/common/args/kube-scheduler`
and set the `--bind-address` to be `127.0.0.1`.

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kube-scheduler <<EOL
--bind-address=127.0.0.1
EOL'
```

Do the same for the Kubernetes controller manager
(`/var/snap/k8s/common/args/kube-controller-manager`):

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kube-controller-manager <<EOL
--bind-address=127.0.0.1
EOL'
```

Restart both services.

```
sudo systemctl restart snap.k8s.kube-scheduler
sudo systemctl restart snap.k8s.kube-controller-manager
```

### Worker nodes

Run the following commands on nodes that host workloads. In the default
deployment the control plane nodes functions as workers and they may need
to be hardened.

#### Protect kernel defaults

<!-- WHAT WORKLOADS? -->

<!-- ADDRESSES V-242434 -->

```{note}
This configuration may affect compatibility of workloads.
```

Kubelet will not start if it finds kernel configurations incompatible with its
 defaults.

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kubelet <<EOL
--protect-kernel-defaults=true
EOL'
```

Restart `kubelet`.

```
sudo systemctl restart snap.k8s.kubelet
```

Reload the system daemons:

```
sudo systemctl daemon-reload
```

#### Edit kubelet service file permissions

<!-- ADDRESSES V-245541 -->
```{note}
Fully complying with the spirit of this hardening recommendation calls for
systemd configuration that is out of the scope of this documentation page.
```

Ensure that only the owner of `/etc/systemd/system/snap.k8s.kubelet.service`
has full read and write access to it. Setting the kubelet service file
permission needs to be performed every time the k8s snap refreshes.

```
chmod 600 /etc/systemd/system/snap.k8s.kubelet.service
```

Restart `kubelet`.

```
sudo systemctl restart snap.k8s.kubelet
```

<!-- DOESN'T SEEM TO CORRELATE TO DISA STIG  -->
#### Set the maximum time an idle session is permitted prior to disconnect

<!-- WHY HAVEN'T WE SET THIS -->

Idle connections from the Kubelet can be used by unauthorized users to
perform malicious activity to the nodes, pods, containers, and cluster within
the Kubernetes Control Plane.

Edit `/var/snap/k8s/common/args/kubelet` and set the argument
`--streaming-connection-idle-timeout` to `5m`.

```
sudo sh -c 'cat >>/var/snap/k8s/common/args/kubelet <<EOL
--streaming-connection-idle-timeout=5m
EOL'
```

Restart `kubelet`.

```
sudo systemctl restart snap.k8s.kubelet
```


## Deploy workloads

## Post cluster checks

After you have deployed your workloads, you must complete a few manual checks to
ensure that the user generated pods adhere to DISA STIG recommendations.

<!-- **USER CHECK WE PASS** -->

## [V-242383] User-managed resources must be created in dedicated namespaces

Manually inspect the services in all of the default namespaces to ensure there
are no user-created resources:

```
kubectl -n default get all | grep -v "^(service|NAME)"
kubectl -n kube-public get all | grep -v "^(service|NAME)"
kubectl -n kube-node-lease get all | grep -v "^(service|NAME)"
```

<!-- I DONT UNDERSTAND HERE WHAT WE ARE RECOMMENDING BESIDES READ UP ON IT YOURSELF -->
## [V-242410],[V-242411],[V-242412] Comply to PPSM CAL

The Kubernetes API Server, Kubernetes Scheduler and Kubernetes Controllers must
enforce ports, protocols, and services (PPS) that adhere to the Ports, Protocols
and Services Management Category Assurance List (PPSM CAL). This must be audited
manually. More information can be found at
[DoD Instruction 8551.01 Policy](https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodi/855101p.pdf)


<!-- **USER ONLY** -->

## [V-242415] Secrets must not be stored as environment variables

Inspect the environment of each user-created pod to ensure there is no
sensitive information (e.g. passwords, cryptographic keys, API tokens, etc).

```
sudo k8s kubectl exec -it PODNAME -n kube-system -- env
```

<!-- **USER CHECKS - WE PASS** -->

## [V-242414] User pods must use non-privileged host ports

Inspect the pods in all of the default namespaces to ensure there are no
user-created pods with containers exposing privileged port numbers (< 1024).

```
kubectl get pods --all-namespaces
kubectl -n NAMESPACE get pod PODNAME -o yaml | grep -i port
```

<!-- **USER ONLY** -->

## [V-242417] Separate functionality of user pods

Inspect the pods in all of the default namespaces to ensure there are no
user-created pods.Move the pods into dedicated user namespaces if present.

```
kubectl -n kube-system get pods
kubectl -n kube-public get pods
kubectl -n kube-node-lease get pods
```


<!-- IN ORDER TO REMOVE THIS AFTER CHECK I THINK WE SHOULD HAVE A BETTER ADVICE ON WHAT ADMISSION CONTROL FILE WE SUGGEST -->
<!-- ## [V-254800]

**Guideline:** Kubernetes must have a Pod Security Admission control file
configured

**Severity:** High

**Class:** Manual

**Upstream finding description:**

> An admission controller intercepts and processes requests to the Kubernetes
> API prior to persistence of the object, but after the request is
> authenticated and authorized.
>
> Kubernetes (> v1.23)offers a built-in Pod Security admission controller to
> enforce the Pod Security Standards. Pod security restrictions are applied at
> the namespace level when pods are created.
>
> The Kubernetes Pod Security Standards define different isolation levels for
> Pods. These standards define how to restrict the behavior of pods in a clear,
> consistent fashion.

**Comments:**

> This Finding stipulates the presence of a Pod Security Admission Control File
> which will need to be manually configured by the Kubernetes System
> Administrator on a per-organization basis.
>
> Instructions on how to configure an `--admission-control-config-file` for the
> Kube API Server of the k8s-snap can be found in the [hardening guide page].
> -->



<!-- SHOULD WE ADD HERE ABOUT WHAT NOT TO DO? WE HAVE NOT APPLICABLE STEPS HERE BUT THAT IS BECAUSE WE DONT ENABLE THINGS. SHOULD WE INCLUDE THESE AS A LIST? -->

<!-- V-242393, V-242394, V-242395, V-242413, V-242454, V-242455 WE COMPLY WITH BECAUSE WE DONT HAVE THESE ENABLED. SHOULD WE SAY DONT DO THESE THINGS? -->

## Full DISA STIG audit

If you would like to manually audit any of the other DISA STIG recommendations,
visit our DISA STIG hardening page.  <!-- link -->

<!-- Links -->
[upstream instructions]:https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/
[rate limits]:https://kubernetes.io/docs/reference/config-api/apiserver-eventratelimit.v1alpha1
[controlling_access]: https://kubernetes.io/docs/concepts/security/controlling-access/
[access_authn_authz]: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
[encryption_at_rest]: https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
[authorization_mode]: https://kubernetes.io/docs/reference/access-authn-authz/authorization/#authorization-modules

