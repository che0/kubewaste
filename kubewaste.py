#!/usr/bin/env python3

import kubernetes
import tabulate
import argparse
import re


class ParseError(Exception):
    pass


def format_cpu(requests, usage):
    def _millis(cpu):
        m = re.match(r"^(\d+(?:\.\d+)?)([mn]?)$", cpu)
        if m is None:
            raise ParseError(cpu)
        number, unit = m.groups()
        return float(number) / {"m": 1000, "n": 1_000_000_000, "": 1}[unit] * 1000

    try:
        req_cpu = _millis(requests["cpu"])
        used_cpu = _millis(usage["cpu"]) if usage is not None else 0
        used_pct = 100 * used_cpu / req_cpu
    except (ParseError, KeyError) as e:
        return [
            requests.get("cpu", "-"),
            usage.get("cpu", "-") if usage is not None else 0,
            f"fail:{e}",
        ]

    return [f"{req_cpu:.0f}m", f"{used_cpu:.0f}m", f"{used_pct:.1f}%"]


def format_memory(requests, usage):
    def _mibibytes(memory):
        m = re.match(r"^(\d+)([KMG]i)$", memory)
        if m is None:
            raise ParseError(memory)
        number, unit = m.groups()
        return (
            float(number)
            * {"Ki": 2**10, "Mi": 2**20, "Gi": 2**30}[unit]
            / 2**20
        )

    try:
        req_mem = _mibibytes(requests["memory"])
        used_mem = _mibibytes(usage["memory"]) if usage is not None else 0
        used_pct = 100 * used_mem / req_mem
    except (ParseError, KeyError) as e:
        return [
            requests.get("memory", "-"),
            usage.get("memory", "-") if usage is not None else 0,
            f"fail:{e}",
        ]

    return [f"{req_mem:.0f}Mi", f"{used_mem:.0f}Mi", f"{used_pct:.1f}%"]


def format_resources(requests, usage):
    return format_cpu(requests, usage) + format_memory(requests, usage)


def get_pods(namespace):
    api = kubernetes.client.CoreV1Api()
    if namespace:
        return api.list_namespaced_pod(namespace)
    else:
        return api.list_pod_for_all_namespaces()


def get_metrics(namespace):
    api = kubernetes.client.CustomObjectsApi()
    if namespace:
        return api.list_namespaced_custom_object(
            "metrics.k8s.io", "v1beta1", namespace, "pods"
        )
    else:
        return api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "pods")


def get_resource_usage(namespace):
    usage = {
        pod["metadata"]["name"]: {
            container["name"]: container["usage"] for container in pod["containers"]
        }
        for pod in get_metrics(namespace)["items"]
    }

    for pod in get_pods(namespace).items:
        if pod.status.phase != "Running":
            continue
        for container in pod.spec.containers:
            yield [pod.metadata.name, container.name] + format_resources(
                container.resources.requests,
                usage.get(pod.metadata.name, {}).get(container.name),
            )


def main():
    parser = argparse.ArgumentParser(
        prog="kubewaste",
        description="Displays pods/containers according to how much requested resources they currently waste",
    )
    parser.add_argument("--context", help="Kubernetes config context to use")
    parser.add_argument("--namespace", "-n", help="Kubernetes namespace to use")
    args = parser.parse_args()

    kubernetes.config.load_config(context=args.context)
    print(
        tabulate.tabulate(
            get_resource_usage(args.namespace),
            headers=[
                "POD",
                "CONTAINER",
                "CPU_REQ",
                "CPU_USED",
                "CPU_PCT",
                "MEM_REQ",
                "MEM_USED",
                "MEM_PCT",
            ],
            tablefmt="plain",
        )
    )


if __name__ == "__main__":
    main()
