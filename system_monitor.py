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

    return cpu_usage, memory.percent, disk.percent, uptime


def get_network_info():
    network_info = psutil.net_if_addrs()

    for interface, addresses in network_info.items():
        print(f"\n{interface}")

        for address in addresses:
            if address.family == 2:
                print(f"  IPv4: {address.address}")


def get_status(usage):
    if usage > 80:
        return "WARNING"
    elif usage >= 70:
        return "NOTICE"
    else:
        return "OK"


def check_warnings(cpu_usage, memory_usage, disk_usage):
    print("\nResource Status:")

    cpu_status = get_status(cpu_usage)
    ram_status = get_status(memory_usage)
    disk_status = get_status(disk_usage)

    print(f"CPU:  {cpu_usage}%  [{cpu_status}]")
    print(f"RAM:  {memory_usage}%  [{ram_status}]")
    print(f"Disk: {disk_usage}%  [{disk_status}]")

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
    print("=" * 50)
    print("        LINUX SYSTEM MONITOR")
    print("=" * 50)

    cpu, ram, disk, uptime = get_system_info()

    print(f"CPU Usage: {cpu}%")
    print(f"RAM Usage: {ram}%")
    print(f"Disk Usage: {disk}%")
    print(f"System Uptime: {uptime}")

    print("\nNetwork Interfaces:")
    get_network_info()

    check_warnings(cpu, ram, disk)


if __name__ == "__main__":
    args = parse_arguments()

    if args.watch:
        watch_mode(args.interval)
    else:
        display_dashboard()