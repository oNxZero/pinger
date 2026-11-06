# Pinger

Terminal ping tool with latency and jitter statistics, configurable packet sizes, and session logs. Requires Python 3.11+, `ping3`, and `colorama`.

## Features

* Latency minimum, maximum, average, and jitter.
* Set packet payload size with `-s`.
* Save timestamped `.txt` logs and session summaries.
* Disable the dashboard with `--quiet` for use in scripts.
* Print a session summary on `Ctrl+C`.
* Display the resolved IP beside the hostname.
* Fixed-width output table.

## Installation

Requires **Python 3.11+**.

```bash
git clone https://github.com/oNxZero/pinger.git
cd pinger
pip install ping3 colorama
```

### Optional: Global CLI (Linux)

```bash
chmod +x pinger.py
sudo mv pinger.py /usr/local/bin/pinger
```

## Usage

### Interactive Mode
```bash
sudo pinger
```

### CLI Mode
```bash
# Basic test
sudo pinger google.com

# MTU test
sudo pinger 1.1.1.1 -s 1500 -i 100 -c 0

# Logging
sudo pinger github.com -c 50 -o results.txt
```

### Automation
```bash
sudo pinger 8.8.8.8 -q -c 0 | grep "DOWN"
```

## Command Flags

| Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| HOST | None | Target IP or hostname | Required |
| -c | --count | Number of pings (0 = infinite) | 8 |
| -i | --interval | Delay between pings (ms) | 500 |
| -t | --timeout | Timeout per ping (ms) | 1000 |
| -s | --size | Payload size (bytes) | 56 |
| -o | --output | Save results to file | None |
| -q | --quiet | Disable UI output | False |

## Output Explained

| Column | Description |
| :--- | :--- |
| TRY | Packet sequence number |
| TARGET | Resolved IP address |
| BYTES | Packet size |
| LATENCY | Round-trip time (ms) |
| STATUS | UP or DOWN |

### Summary

* Packet statistics (sent/received/loss)
* Latency metrics (min/avg/max)
* Jitter (latency variance)

#### Example Summary Output

```
══════════════════════════════════════════════════════════
        Packets: Sent=10, Recv=10, Lost=0 (0.0%)
  Latency: Avg=1.0ms, Min=0.9ms, Max=1.0ms, Jitter=0.0ms
 Log saved to: results.txt
══════════════════════════════════════════════════════════
```

## Requirements & Permissions

Uses raw ICMP sockets:

* **Linux:** Requires `sudo` or `cap_net_raw`
* **Windows:** Run in Administrator terminal

## License

Distributed under the MIT License. See `LICENSE`.
