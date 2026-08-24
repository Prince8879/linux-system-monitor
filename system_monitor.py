import argparse
import datetime
import time
import psutil


def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    current_time = datetime.datetime.now()
    uptime = current_time - boot_time
    uptime = str(uptime).split(".")[0]

    return cpu_usage, memory.percent, disk.percent, uptime


def get_network_info():
    network_info = psutil.net_if_addrs()

    for interface, addresses in network_info.items():
        for address in addresses:
            if address.family == 2:
                ip = address.address

                if ip.startswith("169.254.") or ip == "127.0.0.1":
                    continue

                print(f"{interface:<35}: {ip}")


def get_process_info(limit=10):
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

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.5)

    cpu_count = psutil.cpu_count(logical=True) or 1

    for process in process_objects:
        try:
            cpu_usage = process.cpu_percent(interval=None)

            # Normalize process CPU usage to a 0-100% scale.
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

        except (psutil.NoSuchProcess, psutil.AccessDenied):
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
    print(f"{'PID':<8}{'PROCESS':<25}{'CPU %':>10}{'RAM %':>10}")
    print("-" * 55)

    for process in processes:
        print(
            f"{process['pid']:<8}"
            f"{process['name'][:24]:<25}"
            f"{process['cpu']:>9.2f}%"
            f"{process['memory']:>9.2f}%"
        )


def get_status(usage):
    if usage > 80:
        return "WARNING"
    elif usage >= 70:
        return "NOTICE"
    else:
        return "OK"


def check_warnings(cpu_usage, memory_usage, disk_usage):
    print("\nRESOURCE STATUS")
    print("-" * 55)

    cpu_status = get_status(cpu_usage)
    ram_status = get_status(memory_usage)
    disk_status = get_status(disk_usage)

    print(f"CPU Usage       : {cpu_usage:5.1f}%  [{cpu_status}]")
    print(f"RAM Usage       : {memory_usage:5.1f}%  [{ram_status}]")
    print(f"Disk Usage      : {disk_usage:5.1f}%  [{disk_status}]")

def watch_mode(interval):
    try:
        while True:
            print("\033[2J\033[H")
            display_dashboard()
            print(f"\nRefreshing in {interval} seconds... Press Ctrl+C to stop.")
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

    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("interval must be greater than 0")

    return args


def display_dashboard():
    print("=" * 55)
    print("             LINUX SYSTEM MONITOR")
    print("=" * 55)

    cpu, ram, disk, uptime = get_system_info()

    print("\nSYSTEM OVERVIEW")
    print("-" * 55)

    print(f"CPU Usage       : {cpu:5.1f}%")
    print(f"RAM Usage       : {ram:5.1f}%")
    print(f"Disk Usage      : {disk:5.1f}%")
    print(f"System Uptime   : {uptime}")

    print("\nNETWORK")
    print("-" * 55)

    get_network_info()

    check_warnings(cpu, ram, disk)

    display_processes(10)

    print("\n" + "=" * 55)


if __name__ == "__main__":
    args = parse_arguments()

    if args.watch:
        watch_mode(args.interval)
    else:
        display_dashboard()
