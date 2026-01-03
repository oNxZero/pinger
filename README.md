# Pinger

A terminal-based ping utility built on top of the Python `ping3` library.

I always liked the old Quarantine tool ping utility and wanted something similar, so I ended up building my own version around `ping3`.

It focuses on readable output, basic statistics, and simple usage. It is meant for quick diagnostics and testing, not for continuous monitoring.

## Description

`pinger` uses `ping3` internally to send ICMP echo requests to a host or IP address.  
On top of that, it adds structured table output, packet and latency statistics, colored status indicators, and both command-line and interactive usage.

The tool runs entirely in the terminal and does not rely on the system `ping` binary.

## Dependencies

- Python 3.8 or newer
- ping3
- colorama

Install dependencies with:

    pip install ping3 colorama

## Usage

Command-line usage:

    pinger HOST [-c COUNT] [-i INTERVAL_MS] [-t TIMEOUT_MS]

Examples:

    pinger google.com
    pinger 1.1.1.1 -c 5 -i 200 -t 1000

## Help output

This is the exact help text printed by the program when using `-h` or `--help`:

    Usage:
      pinger HOST [-c COUNT] [-i INTERVAL_MS] [-t TIMEOUT_MS]
      pinger -h | --help

    Flags:
      HOST                  IP address or hostname to ping
      -c,  --count COUNT    Number of pings to send (default: 10)
      -i,  --interval MS    Delay between pings in milliseconds (default: 500)
      -t,  --timeout  MS    Timeout per ping in milliseconds (default: 1000)
      -h,  --help           Show this help and exit

    Examples:
      pinger google.com
      pinger 1.1.1.1 -c 5 -i 200 -t 1000

## Interactive mode

If `pinger` is started without any arguments, it enters interactive mode.

In this mode, the program prompts for:

- host or IP address
- number of pings
- interval between pings
- timeout per ping

All input is validated before execution.

## Output

For each ping attempt, the following fields are displayed:

- attempt number
- target IP or hostname
- protocol (ICMP)
- latency in milliseconds
- packet size
- status (UP / Down)

After all pings complete, a summary is printed containing:

- packets sent
- packets received
- packets lost
- packet loss percentage
- minimum latency
- average latency
- maximum latency

ANSI colors are used to highlight status and values.

## License

Use and modify freely.
