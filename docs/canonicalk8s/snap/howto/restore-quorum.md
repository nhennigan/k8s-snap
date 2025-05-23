# How to recover a cluster after quorum loss

Highly available {{product}} clusters can survive losing one or more
nodes. [Dqlite], the default datastore, implements a [Raft] based protocol
where an elected leader holds the definitive copy of the database, which is
then replicated on two or more secondary nodes.

When the a majority of the nodes are lost, the cluster becomes unavailable.
If at least one database node survived, the cluster can be recovered using the
steps outlined in this document.

```{note}
This guide can be used to recover the default {{product}} datastore,
Dqlite. Persistent volumes on the lost nodes are *not* recovered.
```

Please consult the [Dqlite configuration reference] before moving forward.

## Stop {{product}} services on all nodes

Before recovering the cluster, all remaining {{product}} services
must be stopped. Use the following command on every node:

```
sudo snap stop k8s
```

## Recover the database

Choose one of the remaining alive cluster nodes that has the most recent
version of the Raft log.

Update the ``cluster.yaml`` files, changing the role of the lost nodes to
"spare" (2). Additionally, double check the addresses and IDs specified in
``cluster.yaml``, ``info.yaml`` and ``daemon.yaml``, especially if database
files were moved across nodes.

The following command guides us through the recovery process, prompting a text
editor with informative inline comments for each of the Dqlite configuration
files.

```
sudo /snap/k8s/current/bin/k8sd cluster-recover \
    --state-dir=/var/snap/k8s/common/var/lib/k8sd/state \
    --k8s-dqlite-state-dir=/var/snap/k8s/common/var/lib/k8s-dqlite \
    --log-level 0
```

Please adjust the log level for additional debug messages by increasing its
value. The command creates database backups before making any changes.

The above command will reconfigure the Raft members and create recovery
tarballs that are used to restore the lost nodes, once the Dqlite
configuration is updated.

```{note}
By default, the command will recover both Dqlite databases. If one of the
databases needs to be skipped, use the ``--skip-k8sd`` or ``--skip-k8s-dqlite``
flags. This can be useful when using an external Etcd database.
```

```{note}
Non-interactive mode can be requested using the ``--non-interactive`` flag.
In this case, no interactive prompts or text editors will be displayed and
the command will assume that the configuration files have already been updated.

This allows automating the recovery procedure.
```

Once the "cluster-recover" command completes, restart the k8s services on the
node:

```
sudo snap start k8s
```

Ensure that the services started successfully by using
``sudo snap services k8s``. Use ``sudo k8s status --wait-ready`` to wait for the
cluster to become ready.

You may notice that we have not returned to an HA cluster yet:
``high availability: no``. This is expected as we need to recover
the remaining nodes.

## Recover the remaining nodes

The k8s-dqlite and k8sd recovery tarballs need to be copied over to all cluster
nodes.

For k8sd, copy ``recovery_db.tar.gz`` to
``/var/snap/k8s/common/var/lib/k8sd/state/recovery_db.tar.gz``. When the k8sd
service starts, it will load the archive and perform the necessary recovery
steps.

The k8s-dqlite archive needs to be extracted manually. First, create a backup
of the current k8s-dqlite state directory:

```
sudo mv /var/snap/k8s/common/var/lib/k8s-dqlite \
  /var/snap/k8s/common/var/lib/k8s-dqlite.bkp
```

Then, extract the backup archive:

```
sudo mkdir /var/snap/k8s/common/var/lib/k8s-dqlite
sudo tar xf  recovery-k8s-dqlite-$timestamp-post-recovery.tar.gz \
  -C /var/snap/k8s/common/var/lib/k8s-dqlite
```

Node specific files need to be copied back to the k8s-dqlite state directory:

```
sudo cp /var/snap/k8s/common/var/lib/k8s-dqlite.bkp/cluster.crt \
  /var/snap/k8s/common/var/lib/k8s-dqlite
sudo cp /var/snap/k8s/common/var/lib/k8s-dqlite.bkp/cluster.key \
  /var/snap/k8s/common/var/lib/k8s-dqlite
sudo cp /var/snap/k8s/common/var/lib/k8s-dqlite.bkp/info.yaml \
  /var/snap/k8s/common/var/lib/k8s-dqlite
```

Once these steps are completed, restart the k8s services:

```
sudo snap start k8s
```

Repeat these steps for all remaining nodes. Once a quorum is achieved,
the cluster will be reported as "highly available":

```
$ sudo k8s status
cluster status:           ready
control plane nodes:      10.80.130.168:6400 (voter),
                          10.80.130.167:6400 (voter),
                          10.80.130.164:6400 (voter)
high availability:        yes
datastore:                k8s-dqlite
network:                  enabled
dns:                      enabled at 10.152.183.193
ingress:                  disabled
load-balancer:            disabled
local-storage:            enabled at /var/snap/k8s/common/rawfile-storage
gateway                   enabled
```


<!-- LINKS -->
[Dqlite]: https://dqlite.io/
[Dqlite configuration reference]: ../reference/dqlite.md
[Raft]: https://raft.github.io/
