#!/usr/bin/env python3
"""Minimal validator for eventual Kubernetes resource state in docs spread tests."""

import argparse
import json
import subprocess
import time
from typing import Any

DEFAULT_TIMEOUT = 30
DEFAULT_INTERVAL = 2.0


class ValidationError(Exception):
    pass


def run_kubectl_json(args: list[str]) -> Any:
    cmd = ["sudo", "k8s", "kubectl", *args, "-o", "json"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise ValidationError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON output from {' '.join(cmd)}") from exc


def check_node_ready(name: str) -> bool:
    data = run_kubectl_json(["get", "node", name])
    conditions = data.get("status", {}).get("conditions", [])
    return any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)


def check_pod_ready(namespace: str, name: str) -> bool:
    data = run_kubectl_json(["get", "pod", name, "-n", namespace])

    if data.get("metadata", {}).get("deletionTimestamp"):
        return False

    phase = data.get("status", {}).get("phase")
    if phase not in ("Running", "Succeeded"):
        return False

    conditions = data.get("status", {}).get("conditions", [])
    return any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)


def pod_is_ready(data: dict[str, Any]) -> bool:
    if data.get("metadata", {}).get("deletionTimestamp"):
        return False

    phase = data.get("status", {}).get("phase")
    if phase not in ("Running", "Succeeded"):
        return False

    conditions = data.get("status", {}).get("conditions", [])
    return any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions)


def check_pods_ready_by_label(namespace: str, label: str) -> bool:
    data = run_kubectl_json(["get", "pods", "-n", namespace, "-l", label])
    items = data.get("items", [])
    if not items:
        return False

    return all(pod_is_ready(pod) for pod in items)


def check_pvc_bound(namespace: str, name: str) -> bool:
    data = run_kubectl_json(["get", "pvc", name, "-n", namespace])
    return data.get("status", {}).get("phase") == "Bound"


def check_service_exists(namespace: str, name: str) -> bool:
    _ = run_kubectl_json(["get", "service", name, "-n", namespace])
    return True


def check_gatewayclass_exists(name: str) -> bool:
    _ = run_kubectl_json(["get", "gatewayclass", name])
    return True


def check_k8s_get_contains(key: str, expected: str) -> bool:
    cmd = ["sudo", "k8s", "get", key]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise ValidationError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
    return expected in result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate eventual Kubernetes state")
    parser.add_argument(
        "--check",
        required=True,
        choices=[
            "node-ready",
            "pod-ready",
            "pvc-bound",
            "service-exists",
            "gatewayclass-exists",
            "k8s-get-contains",
        ],
        help="Validation check to run",
    )
    parser.add_argument("--name", help="Resource name")
    parser.add_argument("--label", help="Pod label selector (pod-ready only)")
    parser.add_argument("--key", help="k8s configuration key (for k8s-get-contains)")
    parser.add_argument("--expect", help="Expected substring in readback output")
    parser.add_argument("--namespace", default="default", help="Resource namespace")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="Total seconds to wait before failing",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help="Seconds between retries",
    )
    return parser.parse_args()


def run_check(args: argparse.Namespace) -> bool:
    if args.check == "node-ready":
        if not args.name:
            raise ValidationError("--name is required for node-ready")
        return check_node_ready(args.name)
    if args.check == "pod-ready":
        if args.name and args.label:
            raise ValidationError("Use either --name or --label for pod-ready, not both")
        if args.label:
            return check_pods_ready_by_label(args.namespace, args.label)
        if not args.name:
            raise ValidationError("--name or --label is required for pod-ready")
        return check_pod_ready(args.namespace, args.name)
    if args.check == "pvc-bound":
        if not args.name:
            raise ValidationError("--name is required for pvc-bound")
        return check_pvc_bound(args.namespace, args.name)
    if args.check == "service-exists":
        if not args.name:
            raise ValidationError("--name is required for service-exists")
        return check_service_exists(args.namespace, args.name)
    if args.check == "gatewayclass-exists":
        if not args.name:
            raise ValidationError("--name is required for gatewayclass-exists")
        return check_gatewayclass_exists(args.name)
    if args.check == "k8s-get-contains":
        if not args.key:
            raise ValidationError("--key is required for k8s-get-contains")
        if not args.expect:
            raise ValidationError("--expect is required for k8s-get-contains")
        return check_k8s_get_contains(args.key, args.expect)
    raise ValidationError(f"Unknown check: {args.check}")


def main() -> int:
    args = parse_args()
    attempts = max(1, int(args.timeout / args.interval))

    for attempt in range(1, attempts + 1):
        try:
            if run_check(args):
                print(
                    f"Validation succeeded: check={args.check} name={args.name} "
                    f"label={args.label} namespace={args.namespace}"
                )
                return 0
            print(
                f"Attempt {attempt}/{attempts}: condition not met yet for "
                f"check={args.check} name={args.name} label={args.label}"
            )
        except ValidationError as exc:
            print(f"Attempt {attempt}/{attempts}: {exc}")

        if attempt < attempts:
            time.sleep(args.interval)

    print(
        f"Validation failed after {attempts} attempts: "
        f"check={args.check} name={args.name} label={args.label} namespace={args.namespace}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
