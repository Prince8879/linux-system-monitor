# Linux System Monitor

A lightweight command-line system monitoring tool built with Python and psutil.

## Overview

Linux System Monitor displays important system resource information directly from the terminal.

The project focuses on practical Python, Linux, system administration, CLI development, and DevOps fundamentals.

## Features

- CPU usage monitoring
- RAM usage monitoring
- Disk usage monitoring
- System uptime monitoring
- Network interface information
- IPv4 address detection
- Resource status levels
- CPU, RAM, and Disk warnings
- Continuous monitoring mode
- Configurable refresh interval
- Command-line interface
- Input validation
- Graceful shutdown with Ctrl+C

## Resource Status Levels

The monitor evaluates system resource usage using three status levels:

| Usage     | Status  |
| --------- | ------- |
| Below 70% | OK      |
| 70% - 80% | NOTICE  |
| Above 80% | WARNING |

## Tech Stack

- Python 3.10+
- psutil
- argparse
- Git
- Linux / WSL

## Project Structure

    linux-system-monitor/
    |
    +-- system_monitor.py
    +-- requirements.txt
    +-- README.md
    +-- .gitignore
    +-- venv/                 # Local only, ignored by Git

## Requirements

- Python 3.10 or newer
- pip
- Git
- Linux, WSL, or Windows for development

## Installation

### 1. Clone the repository

    git clone https://github.com/Prince8879/linux-system-monitor.git

### 2. Enter the project directory

    cd linux-system-monitor

### 3. Create a virtual environment

    python -m venv venv

### 4. Activate the virtual environment

#### Windows PowerShell

    .\venv\Scripts\Activate.ps1

#### Linux / WSL

    source venv/bin/activate

### 5. Install dependencies

    pip install -r requirements.txt

## Usage

### Run the monitor

    python system_monitor.py

### Continuous monitoring

    python system_monitor.py --watch

### Custom refresh interval

    python system_monitor.py --watch --interval 3

The interval value must be greater than zero.

### Show help

    python system_monitor.py --help

### Stop continuous monitoring

Press Ctrl+C to stop monitoring.

## Example Output

The following output uses placeholder network information.

    =======================================================
                 LINUX SYSTEM MONITOR
    =======================================================

    SYSTEM OVERVIEW
    -------------------------------------------------------
    CPU Usage       :  18.2%
    RAM Usage       :  65.4%
    Disk Usage      :  42.1%
    System Uptime   : 2 days, 14:25:10

    NETWORK
    -------------------------------------------------------
    Wi-Fi                              : <IPv4_ADDRESS>
    Ethernet                           : <IPv4_ADDRESS>
    vEthernet (WSL)                    : <IPv4_ADDRESS>

    RESOURCE STATUS
    -------------------------------------------------------
    CPU Usage       :  18.2%  [OK]
    RAM Usage       :  65.4%  [OK]
    Disk Usage      :  42.1%  [OK]

    =======================================================

The network addresses shown above are placeholders and are not real system information.

## CLI Options

| Option             | Description                         |
| ------------------ | ----------------------------------- |
| --help             | Display available commands          |
| --watch            | Continuously monitor the system     |
| --interval SECONDS | Set the monitoring refresh interval |

## Privacy and Security

The project does not intentionally store or upload passwords, API keys, authentication tokens, or system credentials.

Runtime system information is displayed locally in the terminal.

Network information is not stored in the repository.

The local virtual environment is excluded from Git using .gitignore.

## Development

This project is being developed as a practical learning project focused on Python, Linux system administration, system monitoring, Git, GitHub, and DevOps fundamentals.

## Future Improvements

- Process monitoring
- Detailed network statistics
- Network traffic monitoring
- CPU temperature monitoring where supported
- Configurable warning thresholds
- Monitoring logs and history
- Export monitoring data
- Improved terminal interface
- Better cross-platform support
- Additional system health metrics

## Project Status

Current version: V0.2

The project is actively under development.

## License

This project is currently intended as an open-source learning project.

A formal license will be added in a future version.
