import argparse
import datetime
import json
import logging
import platform
import time
from pathlib import Path

import psutil


DEFAULT_CPU_WARNING_THRESHOLD = 80
DEFAULT_RAM_WARNING_THRESHOLD = 80
DEFAULT_DISK_WARNING_THRESHOLD = 80

CONFIG_FILE = Path("config.json")

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "monitor.log"

REPORT_DIR = Path("reports")
REPORT_FILE = REPORT_DIR / "system_report.json"


CPU_WARNING_THRESHOLD = DEFAULT_CPU_WARNING_THRESHOLD
RAM_WARNING_THRESHOLD = DEFAULT_RAM_WARNING_THRESHOLD
DISK_WARNING_THRESHOLD = DEFAULT_DISK_WARNING_THRESHOLD


def load_config():
    global CPU_WARNING_THRESHOLD
    global RAM_WARNING_THRESHOLD
    global DISK_WARNING_THRESHOLD

    CPU_WARNING_THRESHOLD = DEFAULT_CPU_WARNING_THRESHOLD
    RAM_WARNING_THRESHOLD = DEFAULT_RAM_WARNING_THRESHOLD
    DISK_WARNING_THRESHOLD = DEFAULT_DISK_WARNING_THRESHOLD

    if not CONFIG_FILE.exists():
        return

    try:
        with CONFIG_FILE.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            config = json.load(file)

        thresholds = config.get("thresholds", {})

        cpu = thresholds.get(
            "cpu",
            DEFAULT_CPU_WARNING_THRESHOLD
        )

        ram = thresholds.get(
            "ram",
            DEFAULT_RAM_WARNING_THRESHOLD
        )

        disk = thresholds.get(
            "disk",
            DEFAULT_DISK_WARNING_THRESHOLD
        )

        if isinstance(cpu, (int, float)) and 0 < cpu <= 100:
            CPU_WARNING_THRESHOLD = cpu

        if isinstance(ram, (int, float)) and 0 < ram <= 100:
            RAM_WARNING_THRESHOLD = ram

        if isinstance(disk, (int, float)) and 0 < disk <= 100:
            DISK_WARNING_THRESHOLD = disk

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        AttributeError,
    ):
        print(
            "Warning: Unable to load config.json. "
            "Using default thresholds."
        )


def setup_logging():
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_system_usage(cpu, ram, disk):
    logging.info(
        f"CPU={cpu:.1f}% | RAM={ram:.1f}% | DISK={disk:.1f}%"
    )


def format_bytes(value):
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(value)

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    boot_time = datetime.datetime.fromtimestamp(
        psutil.boot_time()
    )

    current_time = datetime.datetime.now()

    uptime = current_time - boot_time
    uptime = str(uptime).split(".")[0]

    return {
        "cpu": cpu_usage,
        "ram": memory.percent,
        "disk": disk.percent,
        "uptime": uptime,
        "cpu_cores": psutil.cpu_count(logical=True) or 1,
        "ram_total": memory.total,
        "ram_used": memory.used,
        "ram_available": memory.available,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
    }


def get_network_info():
    network_interfaces = []

    try:
        network_info = psutil.net_if_addrs()
    except (OSError, AttributeError):
        return network_interfaces

    for interface, addresses in network_info.items():
        ipv4_addresses = []

        for address in addresses:
            if address.family == 2:
                ip = address.address

                if ip.startswith("169.254.") or ip == "127.0.0.1":
                    continue

                ipv4_addresses.append(ip)

        if ipv4_addresses:
            network_interfaces.append(
                {
                    "interface": interface,
                    "ipv4": ipv4_addresses,
                }
            )

    return network_interfaces


def display_network_info():
    network_interfaces = get_network_info()

    if not network_interfaces:
        print("Unable to read network interface information.")
        return

    for network in network_interfaces:
        print(
            f"{network['interface']:<35}: "
            f"{', '.join(network['ipv4'])}"
        )


def get_network_stats():
    try:
        stats = psutil.net_io_counters()

        if stats is None:
            return {
                "bytes_sent": 0,
                "bytes_received": 0,
                "packets_sent": 0,
                "packets_received": 0,
            }

        return {
            "bytes_sent": stats.bytes_sent,
            "bytes_received": stats.bytes_recv,
            "packets_sent": stats.packets_sent,
            "packets_received": stats.packets_recv,
        }

    except (OSError, AttributeError):
        return {
            "bytes_sent": 0,
            "bytes_received": 0,
            "packets_sent": 0,
            "packets_received": 0,
        }


def display_network_stats():
    stats = get_network_stats()

    print("\nNETWORK STATISTICS")
    print("-" * 55)

    print(
        f"{'Bytes Sent':<25}: "
        f"{format_bytes(stats['bytes_sent'])}"
    )

    print(
        f"{'Bytes Received':<25}: "
        f"{format_bytes(stats['bytes_received'])}"
    )

    print(
        f"{'Packets Sent':<25}: "
        f"{stats['packets_sent']:,}"
    )

    print(
        f"{'Packets Received':<25}: "
        f"{stats['packets_received']:,}"
    )


def get_network_rates(interval=1):
    if interval <= 0:
        return 0, 0

    try:
        start = psutil.net_io_counters()

        if start is None:
            return 0, 0

        time.sleep(interval)

        end = psutil.net_io_counters()

        if end is None:
            return 0, 0

        upload_rate = max(
            0,
            (end.bytes_sent - start.bytes_sent) / interval
        )

        download_rate = max(
            0,
            (end.bytes_recv - start.bytes_recv) / interval
        )

        return upload_rate, download_rate

    except (OSError, AttributeError):
        return 0, 0


def display_network_rates(interval=1):
    upload_rate, download_rate = get_network_rates(interval)

    print("\nNETWORK SPEED")
    print("-" * 55)

    print(
        f"Upload Rate   : "
        f"{format_bytes(upload_rate)}/s"
    )

    print(
        f"Download Rate : "
        f"{format_bytes(download_rate)}/s"
    )


def get_process_info(limit=10):
    if limit <= 0:
        return []

    processes = []
    process_objects = []

    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):
        try:
            name = process.info["name"] or "Unknown"

            if name == "System Idle Process":
                continue

            process.cpu_percent(interval=None)
            process_objects.append(process)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    time.sleep(0.5)

    cpu_count = psutil.cpu_count(logical=True) or 1

    for process in process_objects:
        try:
            cpu_usage = process.cpu_percent(
                interval=None
            )

            cpu_usage = cpu_usage / cpu_count

            memory_usage = process.memory_percent()

            processes.append(
                {
                    "pid": process.pid,
                    "name": process.name() or "Unknown",
                    "cpu": cpu_usage,
                    "memory": memory_usage,
                }
            )

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess,
        ):
            continue

    processes.sort(
        key=lambda process: process["cpu"],
        reverse=True
    )

    return processes[:limit]


def display_processes(limit=10):
    processes = get_process_info(limit)

    print("\nPROCESS MONITOR")
    print("-" * 55)

    print(
        f"{'PID':<8}"
        f"{'PROCESS':<25}"
        f"{'CPU %':>10}"
        f"{'RAM %':>10}"
    )

    print("-" * 55)

    for process in processes:
        print(
            f"{process['pid']:<8}"
            f"{process['name'][:24]:<25}"
            f"{process['cpu']:>9.2f}%"
            f"{process['memory']:>9.2f}%"
        )


def get_status(usage, warning_threshold=80):
    notice_threshold = warning_threshold * 0.875

    if usage > warning_threshold:
        return "WARNING"

    elif usage >= notice_threshold:
        return "NOTICE"

    else:
        return "OK"


def check_warnings(
    cpu_usage,
    memory_usage,
    disk_usage
):
    print("\nRESOURCE STATUS")
    print("-" * 55)

    cpu_status = get_status(
        cpu_usage,
        CPU_WARNING_THRESHOLD
    )

    ram_status = get_status(
        memory_usage,
        RAM_WARNING_THRESHOLD
    )

    disk_status = get_status(
        disk_usage,
        DISK_WARNING_THRESHOLD
    )

    print(
        f"CPU Usage       : "
        f"{cpu_usage:5.1f}%  [{cpu_status}]"
    )

    print(
        f"RAM Usage       : "
        f"{memory_usage:5.1f}%  [{ram_status}]"
    )

    print(
        f"Disk Usage      : "
        f"{disk_usage:5.1f}%  [{disk_status}]"
    )


def calculate_health_score(cpu, ram, disk):
    def resource_score(usage):
        if usage >= 100:
            return 0

        return max(0, 100 - usage)

    cpu_score = resource_score(cpu)
    ram_score = resource_score(ram)
    disk_score = resource_score(disk)

    score = (
        (cpu_score * 0.35)
        + (ram_score * 0.40)
        + (disk_score * 0.25)
    )

    return round(score)


def get_health_status(score):
    if score >= 80:
        return "GOOD"

    if score >= 60:
        return "NOTICE"

    if score >= 40:
        return "WARNING"

    return "CRITICAL"


def display_health_score(cpu, ram, disk):
    score = calculate_health_score(
        cpu,
        ram,
        disk
    )

    status = get_health_status(score)

    print("\nSYSTEM HEALTH")
    print("-" * 55)

    print(
        f"Overall Health : "
        f"{score}/100 [{status}]"
    )


def display_system_details(info):
    print("\nSYSTEM DETAILS")
    print("-" * 55)

    print(
        f"{'Operating System':<25}: "
        f"{info['os']}"
    )

    print(
        f"{'OS Release':<25}: "
        f"{info['os_release']}"
    )

    print(
        f"{'Machine':<25}: "
        f"{info['machine']}"
    )

    print(
        f"{'Logical CPU Cores':<25}: "
        f"{info['cpu_cores']}"
    )

    print(
        f"{'RAM Total':<25}: "
        f"{format_bytes(info['ram_total'])}"
    )

    print(
        f"{'RAM Used':<25}: "
        f"{format_bytes(info['ram_used'])}"
    )

    print(
        f"{'RAM Available':<25}: "
        f"{format_bytes(info['ram_available'])}"
    )

    print(
        f"{'Disk Total':<25}: "
        f"{format_bytes(info['disk_total'])}"
    )

    print(
        f"{'Disk Used':<25}: "
        f"{format_bytes(info['disk_used'])}"
    )

    print(
        f"{'Disk Free':<25}: "
        f"{format_bytes(info['disk_free'])}"
    )


def build_report():
    info = get_system_info()

    network_stats = get_network_stats()
    network_interfaces = get_network_info()

    processes = get_process_info(10)

    health_score = calculate_health_score(
        info["cpu"],
        info["ram"],
        info["disk"]
    )

    health_status = get_health_status(
        health_score
    )

    report = {
        "timestamp": datetime.datetime.now().isoformat(
            timespec="seconds"
        ),
        "system": {
            "cpu_usage_percent": info["cpu"],
            "ram_usage_percent": info["ram"],
            "disk_usage_percent": info["disk"],
            "uptime": info["uptime"],
            "logical_cpu_cores": info["cpu_cores"],
            "ram_total_bytes": info["ram_total"],
            "ram_used_bytes": info["ram_used"],
            "ram_available_bytes": info["ram_available"],
            "disk_total_bytes": info["disk_total"],
            "disk_used_bytes": info["disk_used"],
            "disk_free_bytes": info["disk_free"],
            "operating_system": info["os"],
            "os_release": info["os_release"],
            "machine": info["machine"],
        },
        "health": {
            "score": health_score,
            "status": health_status,
        },
        "network": {
            "interfaces": network_interfaces,
            "bytes_sent": network_stats["bytes_sent"],
            "bytes_received": network_stats["bytes_received"],
            "packets_sent": network_stats["packets_sent"],
            "packets_received": network_stats["packets_received"],
        },
        "processes": processes,
        "thresholds": {
            "cpu": CPU_WARNING_THRESHOLD,
            "ram": RAM_WARNING_THRESHOLD,
            "disk": DISK_WARNING_THRESHOLD,
        },
    }

    return report


def generate_report():
    REPORT_DIR.mkdir(exist_ok=True)

    report = build_report()

    try:
        with REPORT_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                report,
                file,
                indent=4
            )

        print(
            f"Report generated: {REPORT_FILE}"
        )

        return True

    except OSError as error:
        print(
            f"Unable to generate report: {error}"
        )

        return False


def watch_mode(interval):
    try:
        while True:
            print("\033[2J\033[H")

            display_dashboard()

            print(
                f"\nRefreshing in {interval} seconds..."
                " Press Ctrl+C to stop."
            )

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="A lightweight system monitoring tool."
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously monitor the system."
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        metavar="SECONDS",
        help="Refresh interval in seconds. Default: 5"
    )

    parser.add_argument(
        "--log",
        action="store_true",
        help="Enable local system usage logging."
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a JSON system report."
    )

    args = parser.parse_args()

    if args.interval <= 0:
        parser.error(
            "interval must be greater than 0"
        )

    return args


def display_dashboard():
    print("=" * 55)
    print("             LINUX SYSTEM MONITOR")
    print("=" * 55)

    info = get_system_info()

    cpu = info["cpu"]
    ram = info["ram"]
    disk = info["disk"]
    uptime = info["uptime"]

    if logging.getLogger().hasHandlers():
        log_system_usage(
            cpu,
            ram,
            disk
        )

    print("\nSYSTEM OVERVIEW")
    print("-" * 55)

    print(
        f"CPU Usage       : "
        f"{cpu:5.1f}%"
    )

    print(
        f"RAM Usage       : "
        f"{ram:5.1f}%"
    )

    print(
        f"Disk Usage      : "
        f"{disk:5.1f}%"
    )

    print(
        f"System Uptime   : "
        f"{uptime}"
    )

    display_system_details(info)

    print("\nNETWORK")
    print("-" * 55)

    display_network_info()

    display_network_stats()

    display_network_rates(1)

    check_warnings(
        cpu,
        ram,
        disk
    )

    display_health_score(
        cpu,
        ram,
        disk
    )

    display_processes(10)

    print("\n" + "=" * 55)


if __name__ == "__main__":
    args = parse_arguments()

    load_config()

    if args.log:
        setup_logging()

    if args.report:
        generate_report()

    if args.watch:
        watch_mode(args.interval)

    elif not args.report:
        display_dashboard()
