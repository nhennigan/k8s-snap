#!/usr/bin/env bash
#
# This script collects diagnostics and other relevant information from a Kubernetes
# node (either control-plane or worker node) and compiles them into a tarball report.
# The collected data includes service arguments, Kubernetes cluster info, SBOM, system
# diagnostics, network diagnostics, and more. The script needs to be run with
# elevated permissions (sudo).
#
# Usage:
#   ./inspect.sh [output_file] [--all-namespaces] [--num-snap-log-entries 100000]
#
# Arguments:
#   output_file             (Optional) The full path and filename for the generated tarball.
#                           If not provided, a default filename based on the current date
#                           and time will be used.
#   --all-namespaces        (Optional) Acquire detailed debugging information, including logs
#                           from all Kubernetes namespaces.
#   --num-snap-log-entries  (Optional) The maximum number of log entries to collect
#                           from snap services. Default: 100000.
#   --timeout               (Optional) The maximum time in seconds to wait for a command.
#                           Default: 180s.
#   --core-dump-dir         (Optional) Core dump location. Default: /var/crash.
#
# Example:
#   ./inspect.sh /path/to/output.tar.gz
#   ./inspect.sh  # This will generate a tarball with a default name.
#   ./inspect.sh --all-namespaces  # Obtain logs from all k8s namespaces.

INSPECT_DUMP=$(pwd)/inspection-report
TIMEOUT_LOG="$INSPECT_DUMP"/timeout_warnings.log
# We won't fetch all namespaces by default to avoid logging potentially sensitive
# user data.
ALL_NAMESPACES=0
NUM_SNAP_LOG_ENTRIES=100000
TIMEOUT=180s
CORE_DUMP_DIR="/var/crash"

function log_success {
  printf -- '\033[32m SUCCESS: \033[0m %s\n' "$1"
}

function log_info {
  printf -- '\033[34m INFO: \033[0m %s\n' "$1"
}

function log_warning() {
  printf -- '\033[33m WARNING: \033[0m %s\n' "$1"
}

function log_warning_red {
  printf -- '\033[31m WARNING: \033[0m %s\n' "$1"
}

function is_bootstrapped {
  # If the node is not bootstrapped, the following command will have an exit code 1.
  k8s local-node-status > /dev/null
}

function is_worker_node {
  k8s local-node-status --output-format yaml | grep -q "cluster-role: worker"
}

# Run a command with a timeout. If the command times out, log the command to the
# timeout log file. Returns the exit code of the command, or the 124 exit code.
function run_with_timeout {
  local args=("$@")
  timeout "$TIMEOUT" bash -c "${args[@]}"

  local exit_code=$?

  if [ $exit_code -eq 124 ]; then
    echo "${args[@]}" >>"$TIMEOUT_LOG"
  fi

  return $exit_code
}

function is_service_active {
  local service
  service=$1

  systemctl status "snap.$service" | grep -q "active (running)"
}

function collect_args {
  log_info "Copy service args to the final report tarball"
  cp -r --no-preserve=mode,ownership /var/snap/k8s/common/args "$INSPECT_DUMP"
}

function collect_cluster_info {
  log_info "Copy k8s cluster-info dump to the final report tarball"
  local FLAGS=""
  if [[ "$ALL_NAMESPACES" == "1" ]]; then
    FLAGS="--all-namespaces"
  fi

  run_with_timeout "k8s kubectl cluster-info dump $FLAGS --output-directory $INSPECT_DUMP/cluster-info &>/dev/null"
}

function collect_sbom {
  log_info "Copy SBOM to the final report tarball"
  cp --no-preserve=mode,ownership /snap/k8s/current/bom.json "$INSPECT_DUMP"/sbom.json
}

function collect_system_info {
  mkdir -p $INSPECT_DUMP/sys
  log_info "Copy processes list to the final report tarball"
  ps -ef > $INSPECT_DUMP/sys/ps

  log_info "Copy disk usage information to the final report tarball"
  df -h | grep "^/" &> $INSPECT_DUMP/sys/disk_usage

  log_info "Copy /proc/mounts to the final report tarball"
  cp /proc/mounts $INSPECT_DUMP/sys/proc-mounts

  log_info "Copy memory usage information to the final report tarball"
  free -m > $INSPECT_DUMP/sys/memory_usage

  log_info "Copy swap information to the final report tarball"
  swapon > $INSPECT_DUMP/sys/swap

  log_info "Copy node uptime to the final report tarball"
  uptime > $INSPECT_DUMP/sys/uptime

  log_info "Copy /etc/os-release to the final report tarball"
  cp /etc/os-release $INSPECT_DUMP/sys/etc-os-release

  log_info "Copy loaded kernel modules to the final report tarball"
  lsmod > $INSPECT_DUMP/sys/loaded_kernel_modules

  log_info "Copy dmesg entries"
  dmesg -H > $INSPECT_DUMP/sys/dmesg
}

function collect_k8s_diagnostics {
  log_info "Copy uname to the final report tarball"
  uname -a &>"$INSPECT_DUMP/uname.log"

  log_info "Copy snap diagnostics to the final report tarball"
  snap version &>"$INSPECT_DUMP/snap-version.log"
  snap list k8s &>"$INSPECT_DUMP/snap-list-k8s.log"
  snap services k8s &>"$INSPECT_DUMP/snap-services-k8s.log"
  snap logs k8s -n $NUM_SNAP_LOG_ENTRIES &>"$INSPECT_DUMP/snap-logs-k8s.log"

  log_info "Copy k8s diagnostics to the final report tarball"
  run_with_timeout "k8s kubectl version &>$INSPECT_DUMP/k8s-version.log"
  run_with_timeout "k8s status &>$INSPECT_DUMP/k8s-status.log"
  run_with_timeout "k8s get &>$INSPECT_DUMP/k8s-get.log"
  run_with_timeout "k8s kubectl get cm k8sd-config -n kube-system -o yaml &>$INSPECT_DUMP/k8s.k8sd/k8sd-configmap.log"
  run_with_timeout "k8s kubectl get cm -n kube-system &>$INSPECT_DUMP/k8s-configmaps.log"

  cp --no-preserve=mode,ownership /var/snap/k8s/common/var/lib/k8s-dqlite/cluster.yaml "$INSPECT_DUMP/k8s.k8s-dqlite/k8s-dqlite-cluster.yaml"
  cp --no-preserve=mode,ownership /var/snap/k8s/common/var/lib/k8s-dqlite/info.yaml "$INSPECT_DUMP/k8s.k8s-dqlite/k8s-dqlite-info.yaml"
  cp --no-preserve=mode,ownership /var/snap/k8s/common/var/lib/k8sd/state/database/cluster.yaml "$INSPECT_DUMP/k8s.k8sd/k8sd-cluster.yaml"
  cp --no-preserve=mode,ownership /var/snap/k8s/common/var/lib/k8sd/state/database/info.yaml "$INSPECT_DUMP/k8s.k8sd/k8sd-info.yaml"

  ls -la /var/snap/k8s/common/var/lib/k8s-dqlite &>"$INSPECT_DUMP/k8s.k8s-dqlite/k8s-dqlite-files.log"
  ls -la /var/snap/k8s/common/var/lib/k8sd &>"$INSPECT_DUMP/k8s.k8sd/k8sd-files.log"
}

function collect_service_diagnostics {
  local service
  service=$1

  mkdir -p "$INSPECT_DUMP/$service"

  local status_file
  status_file="$INSPECT_DUMP/$service/systemctl.log"

  systemctl status "snap.$service" &>"$status_file"

  local n_restarts
  n_restarts=$(systemctl show "snap.$service" -p NRestarts | cut -d'=' -f2)

  printf -- "%s -> %s\n" "$service" "$n_restarts" >> "$INSPECT_DUMP/nrestarts.log"

  if [ "$n_restarts" -gt 0 ]; then
    log_warning "Service $service has restarted $n_restarts times due to errors"
  fi

  journalctl -n "$NUM_SNAP_LOG_ENTRIES" -u "snap.$service" &>"$INSPECT_DUMP/$service/journal.log"
}

function collect_registry_mirror_logs {
  local mirror_units=`systemctl list-unit-files --state=enabled | grep "registry-" | awk '{print $1}'`
  if [ -n "$mirror_units" ]; then
    mkdir -p "$INSPECT_DUMP/mirrors"

    for mirror_unit in $mirror_units; do
      journalctl -n 100000 -u "$mirror_unit" &>"$INSPECT_DUMP/mirrors/$mirror_unit.log"
    done
  fi
}

function collect_core_dumps {
  mkdir -p "$INSPECT_DUMP/core_dumps"
  if [[ -d $CORE_DUMP_DIR && ! -z $(ls -A $CORE_DUMP_DIR) ]]; then
    local dump_dir_size=$(du -sh $CORE_DUMP_DIR)
    log_info "Collecting core dumps from $CORE_DUMP_DIR. Size: $dump_dir_size"
    cp $CORE_DUMP_DIR/* "$INSPECT_DUMP/core_dumps/"
  else
    log_info "Core dump directory empty or missing, skipping..."
  fi
}

function collect_network_diagnostics {
  log_info "Copy network diagnostics to the final report tarball"
  ip a &>"$INSPECT_DUMP/ip-a.log" || true
  ip r &>"$INSPECT_DUMP/ip-r.log" || true
  iptables-save &>"$INSPECT_DUMP/iptables.log" || true
  iptables-legacy-save &>"$INSPECT_DUMP/iptables-legacy.log" || true
  ss -plnt &>"$INSPECT_DUMP/ss-plnt.log" || true

  ip6tables-save &>"$INSPECT_DUMP/iptables6.log" || true
  ip6tables-legacy-save &>"$INSPECT_DUMP/iptables6-legacy.log" || true
  ss -plntu &>"$INSPECT_DUMP/ss-plntu.log" || true
  grep -Ei "^(HTTP_PROXY|HTTPS_PROXY|NO_PROXY)=" /etc/environment > "$INSPECT_DUMP/proxy_in_etc_environment"
}

function check_expected_services {
  local services
  services=("$@")

  for service in "${services[@]}"; do
    collect_service_diagnostics "$service"
    if ! is_service_active "$service"; then
      log_info "Service $service is not running"
      log_warning "Service $service should be running on this node"
    else
      log_info "Service $service is running"
    fi
  done
}

function build_report_tarball {
  local output_file
  local now_is
  now_is="$(date +'%Y%m%d_%H%M%S')"

  if [ -z "$1" ]; then
    output_file="$(pwd)/inspection-report-${now_is}.tar.gz"
  else
    output_file="$1"
  fi

  tar -C "$(pwd)" -cf "${output_file%.gz}" inspection-report &>/dev/null
  gzip "${output_file%.gz}" -f
  log_success "Report tarball is at $output_file"
}

if [ "$EUID" -ne 0 ]; then
  printf -- "Elevated permissions are needed for this command. Please use sudo."
  exit 1
fi

POSITIONAL_ARGS=()
while [[ $# -gt 0 ]]; do
  # shellcheck disable=SC2221,SC2222
  case $1 in
    --all-namespaces)
      ALL_NAMESPACES=1
      shift
      ;;
    --num-snap-log-entries)
      shift
      NUM_SNAP_LOG_ENTRIES="$1"
      shift
      ;;
    --timeout)
      shift
      TIMEOUT="$1"
      shift
      ;;
    --core-dump-dir)
      shift
      CORE_DUMP_DIR="$1"
      shift
      ;;
    -*|--*)
      echo "Unknown argument: $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done
set -- "${POSITIONAL_ARGS[@]}"

rm -rf "$INSPECT_DUMP"
mkdir -p "$INSPECT_DUMP"

printf -- 'Collecting service information\n'

control_plane_services=("k8s.containerd" "k8s.kube-proxy" "k8s.k8s-dqlite" "k8s.k8sd" "k8s.kube-apiserver" "k8s.kube-controller-manager" "k8s.kube-scheduler" "k8s.kubelet")
worker_services=("k8s.containerd" "k8s.k8s-apiserver-proxy" "k8s.kubelet" "k8s.k8sd" "k8s.kube-proxy")

if is_worker_node; then
  printf -- 'Running inspection on a worker node\n'
  printf -- 'Inspection ran on a worker node.' >"$INSPECT_DUMP/is-worker-node"
  check_expected_services "${worker_services[@]}"
else
  if is_bootstrapped; then
    printf -- 'Running inspection on a control-plane node\n'
    printf -- 'Inspection ran on a control plane node.' >"$INSPECT_DUMP/is-control-plane-node"
  else
    printf -- 'Running inspection on a node that is not bootstrapped.\n'
    printf -- 'Inspection ran on a node that is not bootstrapped.' >"$INSPECT_DUMP/is-not-bootstrapped-node"
  fi
  check_expected_services "${control_plane_services[@]}"
fi

printf -- 'Collecting registry mirror logs\n'
collect_registry_mirror_logs

printf -- 'Collecting service arguments\n'
collect_args

printf -- 'Collecting k8s cluster-info\n'
collect_cluster_info

printf -- 'Collecting SBOM\n'
collect_sbom

printf -- 'Collecting system information\n'
collect_system_info

collect_core_dumps

printf -- 'Collecting snap and related information\n'
collect_k8s_diagnostics

printf -- 'Collecting networking information\n'
collect_network_diagnostics

if [ -f "$TIMEOUT_LOG" ]; then
  timeout_count=$(wc -l <"$TIMEOUT_LOG")
  if [ "$timeout_count" -gt 0 ]; then
    log_warning "$(printf '%d commands timed out. See %s for details.' "$timeout_count" "$TIMEOUT_LOG")"
  fi
fi

matches=$(grep -rlEi "BEGIN CERTIFICATE|PRIVATE KEY" inspection-report)
if [ -n "$matches" ]; then
  matches_comma_separated=$(echo "$matches" | tr '\n' ',')
  log_warning_red 'Unexpected private key or certificate found in the report:'
  log_warning_red "Found in the following files: ${matches_comma_separated%,}"
  log_warning_red 'Please remove the private key or certificate from the report before sharing.'
fi

printf -- 'Building the report tarball\n'
build_report_tarball "$1"
