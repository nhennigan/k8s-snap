#
# Copyright 2025 Canonical, Ltd.
#
import json
import os
from pathlib import Path

DIR = Path(__file__).absolute().parent

# The following defaults are used to define how long to wait for a condition to be met.
DEFAULT_WAIT_RETRIES = int(os.getenv("TEST_DEFAULT_WAIT_RETRIES") or 120)
DEFAULT_WAIT_DELAY_S = int(os.getenv("TEST_DEFAULT_WAIT_DELAY_S") or 5)

MANIFESTS_DIR = DIR / ".." / ".." / "templates"
CLOUD_INIT_DIR = MANIFESTS_DIR / "cloud-init"

# ETCD_DIR contains all templates required to setup an etcd database.
ETCD_DIR = MANIFESTS_DIR / "etcd"

# ETCD_URL is the url from which the etcd binaries should be downloaded.
ETCD_URL = os.getenv("ETCD_URL") or "https://github.com/etcd-io/etcd/releases/download"

# ETCD_VERSION is the version of etcd to use.
ETCD_VERSION = os.getenv("ETCD_VERSION") or "v3.4.34"

# REGISTRY_DIR contains all templates required to setup an registry mirror.
REGISTRY_DIR = MANIFESTS_DIR / "registry"

# REGISTRY_URL is the url from which the registry binary should be downloaded.
REGISTRY_URL = (
    os.getenv("REGISTRY_URL")
    or "https://github.com/distribution/distribution/releases/download"
)

# REGISTRY_VERSION is the version of registry to use.
REGISTRY_VERSION = os.getenv("REGISTRY_VERSION") or "v2.8.3"

# FLAVOR is the flavor of the snap to use.
FLAVOR = os.getenv("TEST_FLAVOR") or "classic"

# SNAP is the absolute path to the snap against which we run the integration tests.
SNAP = os.getenv("TEST_SNAP")

# SNAP_NAME is the name of the snap under test.
SNAP_NAME = os.getenv("TEST_SNAP_NAME") or "k8s"

# SUBSTRATE is the substrate to use for running the integration tests.
# One of 'lxd' (default), 'juju', or 'multipass'.
SUBSTRATE = os.getenv("TEST_SUBSTRATE") or "lxd"

# SKIP_CLEANUP can be used to prevent machines to be automatically destroyed
# after the tests complete.
SKIP_CLEANUP = (os.getenv("TEST_SKIP_CLEANUP") or "") == "1"

# Note that when using containers, this will override the host configuration.
CORE_DUMP_PATTERN = (os.getenv("TEST_CORE_DUMP_PATTERN")) or r"core-%e.%p.%h"
CORE_DUMP_DIR = (os.getenv("TEST_CORE_DUMP_DIR")) or "/var/crash"

# INSPECTION_REPORTS_DIR is the directory where inspection reports are stored.
# If empty, no reports are generated.
INSPECTION_REPORTS_DIR = os.getenv("TEST_INSPECTION_REPORTS_DIR")

# LXD_PROFILE_NAME is the profile name to use for LXD containers.
LXD_PROFILE_NAME = os.getenv("TEST_LXD_PROFILE_NAME") or "k8s-integration"

# LXD_PROFILE is the profile to use for LXD containers.
LXD_PROFILE = (
    os.getenv("TEST_LXD_PROFILE")
    or (DIR / ".." / ".." / "lxd-profile.yaml").read_text()
)

# LXD_DUALSTACK_NETWORK is the network to use for LXD containers with dualstack configured.
LXD_DUALSTACK_NETWORK = os.getenv("TEST_LXD_DUALSTACK_NETWORK") or "dualstack-br0"

# LXD_DUALSTACK_PROFILE_NAME is the profile name to use for LXD containers with dualstack configured.
LXD_DUALSTACK_PROFILE_NAME = (
    os.getenv("TEST_LXD_DUALSTACK_PROFILE_NAME") or "k8s-integration-dualstack"
)

# LXD_DUALSTACK_PROFILE is the profile to use for LXD containers with dualstack configured.
LXD_DUALSTACK_PROFILE = (
    os.getenv("TEST_LXD_DUALSTACK_PROFILE")
    or (DIR / ".." / ".." / "lxd-dualstack-profile.yaml").read_text()
)

# LXD_IPV6_NETWORK is the network to use for LXD containers with ipv6-only configured.
LXD_IPV6_NETWORK = os.getenv("TEST_LXD_IPV6_NETWORK") or "ipv6-br0"

# LXD_IPV6_PROFILE_NAME is the profile name to use for LXD containers with ipv6-only configured.
LXD_IPV6_PROFILE_NAME = (
    os.getenv("TEST_LXD_IPV6_PROFILE_NAME") or "k8s-integration-ipv6"
)

# LXD_IPV6_PROFILE is the profile to use for LXD containers with ipv6-only configured.
LXD_IPV6_PROFILE = (
    os.getenv("TEST_LXD_IPV6_PROFILE")
    or (DIR / ".." / ".." / "lxd-ipv6-profile.yaml").read_text()
)

# LXD_IMAGE is the image to use for LXD containers.
LXD_IMAGE = os.getenv("TEST_LXD_IMAGE") or "ubuntu:22.04"

# LXD_SIDELOAD_IMAGES_DIR is an optional directory with OCI images from the host
# that will be mounted at /var/snap/k8s/common/images on the LXD containers.
LXD_SIDELOAD_IMAGES_DIR = os.getenv("TEST_LXD_SIDELOAD_IMAGES_DIR") or ""

# MULTIPASS_IMAGE is the image to use for Multipass VMs.
MULTIPASS_IMAGE = os.getenv("TEST_MULTIPASS_IMAGE") or "22.04"

# MULTIPASS_CPUS is the number of cpus for Multipass VMs.
MULTIPASS_CPUS = os.getenv("TEST_MULTIPASS_CPUS") or "2"

# MULTIPASS_MEMORY is the memory for Multipass VMs.
MULTIPASS_MEMORY = os.getenv("TEST_MULTIPASS_MEMORY") or "4G"

# MULTIPASS_DISK is the disk size for Multipass VMs.
MULTIPASS_DISK = os.getenv("TEST_MULTIPASS_DISK") or "20G"

# MULTIPASS_CLOUD_INIT is the cloud-init script to use for Multipass VMs.
# It is the file name in the CLOUD_INIT_DIR directory.
# Environment variables will be replaced before the file is used.
MULTIPASS_CLOUD_INIT = os.getenv("TEST_MULTIPASS_CLOUD_INIT") or ""

# JUJU_MODEL is the Juju model to use.
JUJU_MODEL = os.getenv("TEST_JUJU_MODEL")

# JUJU_CONTROLLER is the Juju controller to use.
JUJU_CONTROLLER = os.getenv("TEST_JUJU_CONTROLLER")

# JUJU_CONSTRAINTS is the constraints to use when creating Juju machines.
JUJU_CONSTRAINTS = os.getenv("TEST_JUJU_CONSTRAINTS", "mem=4G cores=2 root-disk=20G")

# JUJU_BASE is the base OS to use when creating Juju machines.
JUJU_BASE = os.getenv("TEST_JUJU_BASE") or "ubuntu@22.04"

# JUJU_MACHINES is a list of existing Juju machines to use.
JUJU_MACHINES = os.getenv("TEST_JUJU_MACHINES") or ""

# A list of space-separated channels for which the upgrade tests should be run in sequential order.
# First entry is the bootstrap channel. Afterwards, upgrades are done in order.
# Alternatively, use 'recent <num> <flavour>' to get the latest <num> channels for <flavour>.
VERSION_UPGRADE_CHANNELS = (
    os.environ.get("TEST_VERSION_UPGRADE_CHANNELS", "").strip().split()
)

# The minimum Kubernetes release to upgrade from (e.g. "1.31")
# Only relevant when using 'recent' in VERSION_UPGRADE_CHANNELS.
VERSION_UPGRADE_MIN_RELEASE = os.environ.get("TEST_VERSION_UPGRADE_MIN_RELEASE")

# Same usage as VERSION_UPGRADE_MIN_RELEASE but for downgrades.
VERSION_DOWNGRADE_CHANNELS = (
    os.environ.get("TEST_VERSION_DOWNGRADE_CHANNELS", "").strip().split()
)

# A list of space-separated channels for which the strict interface tests should be run in sequential order.
# Alternatively, use 'recent <num> strict' to get the latest <num> channels for strict.
STRICT_INTERFACE_CHANNELS = (
    os.environ.get("TEST_STRICT_INTERFACE_CHANNELS", "").strip().split()
)

# Cache and preload certain snaps such as snapd and core22 to avoid fetching them
# for every test instance. Note that k8s-snap is currently based on core22.
PRELOAD_SNAPS = (os.getenv("TEST_PRELOAD_SNAPS") or "1") == "1"

# The following snaps will be downloaded once per test run and preloaded
# into the harness instances to reduce the number of downloads.
DEFAULT_PRELOADED_SNAPS = ["snapd", "core22"]
PRELOADED_SNAPS = (
    os.getenv("TEST_PRELOADED_SNAPS", "").strip().split() or DEFAULT_PRELOADED_SNAPS
)

# Setup a local image mirror to reduce the number of image pulls. The mirror
# will be configured to run in a session scoped harness instance (e.g. LXD container)
USE_LOCAL_MIRROR = (os.getenv("TEST_USE_LOCAL_MIRROR") or "1") == "1"

DEFAULT_MIRROR_LIST = [
    {"name": "ghcr.io", "port": 5000, "remote": "https://ghcr.io"},
    {"name": "docker.io", "port": 5001, "remote": "https://registry-1.docker.io"},
    {
        "name": "rocks.canonical.com",
        "port": 5002,
        "remote": "https://rocks.canonical.com/cdk",
    },
]

# Local mirror configuration.
MIRROR_LIST = json.loads(os.getenv("TEST_MIRROR_LIST", "{}")) or DEFAULT_MIRROR_LIST

# The GitHub ref_name.
GH_REF = os.getenv("TEST_GH_REF")

# The GitHub base_ref.
GH_BASE_REF = os.getenv("TEST_GH_BASE_REF")

# SONOBUOY_VERSION is the version of sonobuoy to use for CNCF conformance tests.
SONOBUOY_VERSION = os.getenv("TEST_SONOBUOY_VERSION") or "v0.57.3"
