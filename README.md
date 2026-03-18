# 📡 Pinger: Professional Terminal Connectivity Tester

> **A high-performance, async network diagnostic tool with a modern dashboard interface.**

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)

**Pinger** transforms traditional ping output into a structured, real-time diagnostic dashboard. Designed for sysadmins, developers, and power users, it delivers deeper network insight with features like **jitter analysis**, **MTU testing**, and **session logging**—all in a clean, readable interface.

---

## 🚀 Key Features

* **Advanced Metrics:** Latency tracking (Min/Max/Avg) plus **Network Jitter** for stability analysis.
* **MTU & Payload Testing:** Detect fragmentation and VPN issues using custom packet sizes (`-s`).
* **Professional Logging:** Export structured `.txt` logs with timestamps and summaries.
* **Headless Mode:** Use `--quiet` for raw output—ideal for pipelines and automation.
* **Graceful Interrupts:** Safe exit with `Ctrl+C`, including full session summary.
* **Smart DNS Resolution:** Displays resolved IP alongside hostname.
* **Stable UI Rendering:** Fixed-width table prevents layout shifts.

---

## ✨ Why use this?

* **Readable Output:** Clean table format instead of noisy terminal logs.
* **Automation Friendly:** Designed for scripting and monitoring workflows.
* **Deeper Diagnostics:** Jitter + MTU testing go beyond standard ping tools.
* **Flexible Workflow:** Interactive wizard or direct CLI usage.

---

## 📦 Installation

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

---

## 📖 Usage

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

---

## ⚙️ Command Flags

| Flag | Long Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| HOST | None | Target IP or hostname | Required |
| -c | --count | Number of pings (0 = infinite) | 8 |
| -i | --interval | Delay between pings (ms) | 500 |
| -t | --timeout | Timeout per ping (ms) | 1000 |
| -s | --size | Payload size (bytes) | 56 |
| -o | --output | Save results to file | None |
| -q | --quiet | Disable UI output | False |

---

## 📊 Output Explained

| Column | Description |
| :--- | :--- |
| TRY | Packet sequence number |
| TARGET | Resolved IP address |
| BYTES | Packet size |
| LATENCY | Round-trip time (ms) |
| STATUS | UP or DOWN |

### Summary Includes

* Packet statistics (sent/received/loss)
* Latency metrics (min/avg/max)
* Jitter (latency variance)

#### Example Summary Output

```
══════════════════════════════════════════════════════════
        Packets: Sent=10, Recv=10, Lost=0 (0.0%)
  Latency: Avg=1.0ms, Min=0.9ms, Max=1.0ms, Jitter=0.0ms
 📄 Log saved to: /home/bttw/Downloads/my_network_test.tx
══════════════════════════════════════════════════════════
```

---

## 📜 Requirements & Permissions

Uses raw ICMP sockets:

* **Linux:** Requires `sudo` or `cap_net_raw`
* **Windows:** Run in Administrator terminal

---

## 🛡️ License

Distributed under the MIT License. See `LICENSE`.

---
