package app

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"net"
	"os"

	apiv1_annotations "github.com/canonical/k8s-snap-api/api/v1/annotations"
	databaseutil "github.com/canonical/k8s/pkg/k8sd/database/util"
	"github.com/canonical/k8s/pkg/k8sd/pki"
	"github.com/canonical/k8s/pkg/k8sd/setup"
	"github.com/canonical/k8s/pkg/k8sd/types"
	"github.com/canonical/k8s/pkg/log"
	"github.com/canonical/k8s/pkg/snap"
	snaputil "github.com/canonical/k8s/pkg/snap/util"
	"github.com/canonical/k8s/pkg/snap/util/cleanup"
	"github.com/canonical/k8s/pkg/utils"
	"github.com/canonical/k8s/pkg/utils/control"
	"github.com/canonical/microcluster/v2/cluster"
	"github.com/canonical/microcluster/v2/state"
)

// NOTE(ben): the pre-remove performs a series of cleanup steps on a best-effort basis.
// If any step fails, the error is logged, and the cleanup continues, skipping dependent tasks.
// All steps need to be blocking as the context is cancelled after the hook returned.
func (a *App) onPreRemove(ctx context.Context, s state.State, force bool) (rerr error) {
	snap := a.Snap()

	log := log.FromContext(ctx).WithValues("hook", "preremove", "node", s.Name())
	log.Info("Running preremove hook")

	log.Info("Waiting for node to finish microcluster join before removing")
	// NOTE (hue): in microcluster v2, PreRemove hook is also called if something goes wrong on
	// `bootstrap` and `join-cluster`. It is possible that we get stuck in this loop forever which causes
	// the `bootstrap` and `join-cluster` commands to hang and finally return an uninformative `context deadline exceeded` error
	// we optimistically stop trying after a fixed number of retries.
	maxRetries := 10
	var txnRetries int
	if err := control.WaitUntilReady(ctx, func() (bool, error) {
		var notPending bool
		if err := s.Database().Transaction(ctx, func(ctx context.Context, tx *sql.Tx) error {
			member, err := cluster.GetCoreClusterMember(ctx, tx, s.Name())
			if err != nil {
				log.Error(err, "Failed to get member")
				return nil
			}
			notPending = member.Role != cluster.Pending
			return nil
		}); err != nil {
			log.Error(err, "Failed database transaction to check cluster member role")
			txnRetries++
		}

		if txnRetries >= maxRetries {
			log.Info("Reached maximum number of retries for database transactions on pre-remove hook, continuing cleanup", "max_retries", maxRetries)
			return true, nil
		}

		return notPending, nil
	}); err != nil {
		log.Error(err, "Failed to wait for node to finish microcluster join before removing. Continuing with the cleanup...")
	}

	cfg, err := databaseutil.GetClusterConfig(ctx, s)
	if err == nil {
		if _, ok := cfg.Annotations.Get(apiv1_annotations.AnnotationSkipCleanupKubernetesNodeOnRemove); !ok {
			c, err := snap.KubernetesClient("")
			if err != nil {
				log.Error(err, "Failed to create Kubernetes client", err)
			}

			if c != nil {
				log.Info("Deleting node from Kubernetes cluster")
				if err := c.DeleteNode(ctx, s.Name()); err != nil {
					log.Error(err, "Failed to remove Kubernetes node")
				}
			}
		}

		switch cfg.Datastore.GetType() {
		case "k8s-dqlite":
			client, err := snap.K8sDqliteClient(ctx)
			if err == nil {
				log.Info("Removing node from k8s-dqlite cluster")
				nodeAddress := net.JoinHostPort(s.Address().Hostname(), fmt.Sprintf("%d", cfg.Datastore.GetK8sDqlitePort()))
				if err := client.RemoveNodeByAddress(ctx, nodeAddress); err != nil {
					// Removing the node might fail (e.g. if it is the only one in the cluster).
					// We still want to continue with the file cleanup, hence we only log the error.
					log.Error(err, "Failed to remove node from k8s-dqlite cluster")
				}
			} else {
				log.Error(err, "Failed to create k8s-dqlite client: %w")
			}
		case "etcd":
			if err := removeEtcdNode(ctx, snap, s, cfg); err != nil {
				log.Error(err, "Failed to remove node from etcd cluster")
			}
		case "external":
			log.Info("Cleaning up external datastore certificates")
			if _, err := setup.EnsureExtDatastorePKI(snap, &pki.ExternalDatastorePKI{}); err != nil {
				log.Error(err, "Failed to cleanup external datastore certificates")
			}
		default:
		}
	} else {
		log.Error(err, "Failed to retrieve cluster config")
	}

	log.Info("Cleaning up etcd directory")
	if err := os.RemoveAll(snap.EtcdDir()); err != nil {
		log.Error(err, "failed to cleanup etcd state directory")
	}

	log.Info("Cleaning up k8s-dqlite directory")
	if err := os.RemoveAll(snap.K8sDqliteStateDir()); err != nil {
		log.Error(err, "failed to cleanup k8s-dqlite state directory")
	}
	for _, dir := range []string{snap.ServiceArgumentsDir()} {
		log.WithValues("directory", dir).Info("Cleaning up config files", dir)
		if err := os.RemoveAll(dir); err != nil {
			log.WithValues("dir", dir).Error(err, "failed to delete config files", err)
		}
	}

	log.Info("Removing worker node mark")
	if err := snaputil.MarkAsWorkerNode(snap, false); err != nil {
		if !errors.Is(err, os.ErrNotExist) {
			log.Error(err, "failed to unmark node as worker")
		}
	}

	// NOTE(claudiub): We should only remove the certificates only if we're stopping the Kubernetes
	// services as well. Removing them without stopping the services will result in the services
	// being paralyzed and unable to continue their function, including potential Pod evictions
	// started by CAPI.
	if _, ok := cfg.Annotations.Get(apiv1_annotations.AnnotationSkipStopServicesOnRemove); !ok {
		// Perform all cleanup steps regardless of if this is a worker node or control plane.
		// Trying to detect the node type is not reliable as the node might have been marked as worker
		// or not, depending on which step it failed.
		log.Info("Cleaning up worker certificates")
		if _, err := setup.EnsureWorkerPKI(snap, &pki.WorkerNodePKI{}); err != nil {
			log.Error(err, "failed to cleanup worker certificates")
		}

		log.Info("Cleaning up control plane certificates")
		if _, err := setup.EnsureControlPlanePKI(snap, &pki.ControlPlanePKI{}); err != nil {
			log.Error(err, "failed to cleanup control plane certificates")
		}

		log.Info("Stopping all services except k8sd")
		if err := snaputil.StopK8sServices(ctx, snap, "--no-wait"); err != nil {
			log.Error(err, "failed to stop k8s services")
		}

		log.Info("Cleaning up containers")
		cleanup.TryCleanupContainers(ctx, snap)

		log.Info("Cleaning up containerd paths")
		cleanup.TryCleanupContainerdPaths(ctx, snap)
	} else {
		log.Info("Skipping service stop and certificate cleanup")
	}

	log.Info("Remove hook completed ")
	return nil
}

func removeEtcdNode(ctx context.Context, snap snap.Snap, s state.State, cfg types.ClusterConfig) error {
	leader, err := s.Leader()
	if err != nil {
		return fmt.Errorf("failed to get microcluster leader: %w", err)
	}
	members, err := leader.GetClusterMembers(ctx)
	if err != nil {
		return fmt.Errorf("failed to get microcluster members: %w", err)
	}
	clientURLs := make([]string, 0, len(members)-1)
	for _, member := range members {
		if member.Name == s.Name() {
			// skip self
			continue
		}
		clientURLs = append(clientURLs, fmt.Sprintf("https://%s", utils.JoinHostPort(member.Address.Addr().String(), cfg.Datastore.GetEtcdPort())))
	}

	client, err := snap.EtcdClient(clientURLs)
	if err != nil {
		return fmt.Errorf("failed to create etcd client: %w", err)
	}
	defer client.Close()

	nodeAddress := fmt.Sprintf("https://%s", utils.JoinHostPort(s.Address().Hostname(), cfg.Datastore.GetEtcdPeerPort()))
	if err := client.RemoveNodeByAddress(ctx, nodeAddress); err != nil {
		return fmt.Errorf("failed to remove node with address %s from etcd cluster: %w", nodeAddress, err)
	}

	return nil
}
