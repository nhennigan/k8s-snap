# Configuration files for Kubernetes components

The following tables provide an overview of the configuration files used to
communicate with the cluster services.

### Control-plane node

Control-plane nodes use the following configuration files.

| **Configuration File**    | **Purpose**                      | **File Location**                         | **Primary Function**                                |
|---------------------------|----------------------------------|-------------------------------------------|-----------------------------------------------------|
| `admin.conf`              | Administrator Client Config      | `/etc/kubernetes/admin.conf`              | Admin access to the cluster                         |
| `controller-manager.conf` | Controller Manager Client Config | `/etc/kubernetes/controller-manager.conf` | Communication with the API server                   |
| `scheduler.conf`          | Scheduler Client Config          | `/etc/kubernetes/scheduler.conf`          | Communication with the API server                   |
| `kubelet.conf`            | Kubelet Client Config            | `/etc/kubernetes/kubelet.conf`            | Node registration and communication with API server |
| `proxy.conf`              | Proxy Client Config              | `/etc/kubernetes/proxy.conf`              | Communication with the API server                   |

### Worker node

Worker nodes use the following configuration files.

| **Configuration File** | **Purpose**           | **File Location**              | **Primary Function**                                |
|------------------------|-----------------------|--------------------------------|-----------------------------------------------------|
| `proxy.conf`           | Proxy Client Config   | `/etc/kubernetes/proxy.conf`   | Communication with the API server                   |
| `kubelet.conf`         | Kubelet Client Config | `/etc/kubernetes/kubelet.conf` | Node registration and communication with API server |
