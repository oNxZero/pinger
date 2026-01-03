import asyncio
import os
import socket
import sys
import re
import argparse
import shutil
from ping3 import ping
from statistics import mean
from colorama import init, Fore, Style

init(autoreset=True)

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

HELP_TEXT = """Usage:
  pinger HOST [-c COUNT] [-i INTERVAL_MS] [-t TIMEOUT_MS]
  pinger -h | --help

Flags:
  HOST                  IP address or hostname to ping
  -c,  --count COUNT    Number of pings to send (default: 8)
  -i,  --interval MS    Delay between pings in milliseconds (default: 500)
  -t,  --timeout  MS    Timeout per ping in milliseconds (default: 1000)
  -h,  --help           Show this help and exit
"""

def get_term_size():
    return shutil.get_terminal_size((80, 24))

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def print_centered(text, width=None):
    if width is None:
        width = get_term_size().columns
    clean = strip_ansi(text)
    padding = max(0, (width - len(clean)) // 2)
    print(" " * padding + text)

def input_centered(prompt, width=None):
    if width is None:
        width = get_term_size().columns
    clean = strip_ansi(prompt)
    padding = max(0, (width - len(clean)) // 2)
    return input(" " * padding + prompt)

def calc_vertical_margin(content_lines):
    h = get_term_size().lines
    margin = max(0, (h - content_lines) // 2)
    return margin

def parse_args():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("host", nargs="?")
    p.add_argument("-c", "--count", type=int, default=8)
    p.add_argument("-i", "--interval", type=int, default=500)
    p.add_argument("-t", "--timeout", type=int, default=1000)
    p.add_argument("-h", "--help", action="store_true")
    return p.parse_args()

class PingStats:
    def __init__(self):
        self.latencies = []
        self.sent = 0
        self.received = 0

    def add(self, latency):
        self.sent += 1
        if latency is not None:
            self.received += 1
            self.latencies.append(latency * 1000)

    def packet_loss(self):
        return ((self.sent - self.received) / self.sent) * 100 if self.sent else 0

    def avg_latency(self):
        return mean(self.latencies) if self.latencies else 0

    def min_latency(self):
        return min(self.latencies) if self.latencies else 0

    def max_latency(self):
        return max(self.latencies) if self.latencies else 0

def is_valid_ip(host):
    if not host: return False
    if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host):
        return True
    try:
        if len(host) > 1 and "." in host:
            return True
    except:
        pass
    return True

COL_WIDTHS = {
    'try': 8,
    'ip': 25,
    'protocol': 10,
    'latency': 14,
    'bytes': 10,
    'status': 12
}

async def ping_target(host, count=8, interval=0.5, timeout=1.0):
    clear_screen()
    stats = PingStats()

    total_content_height = 3 + count + 5
    top_margin = calc_vertical_margin(total_content_height)

    print("\n" * top_margin)

    header_raw = (
        f"{'TRY'.center(COL_WIDTHS['try'])}"
        f"{'TARGET'.center(COL_WIDTHS['ip'])}"
        f"{'PROTOCOL'.center(COL_WIDTHS['protocol'])}"
        f"{'LATENCY'.center(COL_WIDTHS['latency'])}"
        f"{'BYTES'.center(COL_WIDTHS['bytes'])}"
        f"{'STATUS'.center(COL_WIDTHS['status'])}"
    )
    print_centered(f"{Fore.WHITE}{header_raw}{Style.RESET_ALL}")
    print_centered(f"{Fore.WHITE}{'─' * len(header_raw)}{Style.RESET_ALL}")

    for i in range(count):
        latency = await asyncio.to_thread(ping, host, timeout=timeout)
        stats.add(latency)

        if latency is None:
            status_txt = "Down"
            status_col = f"{Fore.RED}{status_txt.center(COL_WIDTHS['status'])}{Style.RESET_ALL}"
            lat_disp = "-"
            bytes_disp = "-"
        else:
            status_txt = "UP"
            status_col = f"{Fore.WHITE}{status_txt.center(COL_WIDTHS['status'])}{Style.RESET_ALL}"
            lat_disp = f"{latency*1000:.2f} ms"
            bytes_disp = "64"

        row_raw = (
            f"{('#' + str(i+1)).center(COL_WIDTHS['try'])}"
            f"{host.center(COL_WIDTHS['ip'])}"
            f"{'ICMP'.center(COL_WIDTHS['protocol'])}"
            f"{lat_disp.center(COL_WIDTHS['latency'])}"
            f"{bytes_disp.center(COL_WIDTHS['bytes'])}"
        )

        full_vis = row_raw + status_txt.center(COL_WIDTHS['status'])
        w = get_term_size().columns
        pad = max(0, (w - len(full_vis)) // 2)

        print(" " * pad + row_raw + status_col)

        await asyncio.sleep(interval)

    sep = '═' * 80
    print_centered(f"{Fore.WHITE}{sep}{Style.RESET_ALL}")

    s_line1 = (
        f"Packets: {Fore.WHITE}Sent={Fore.YELLOW}{stats.sent}{Style.RESET_ALL}, "
        f"Received={Fore.GREEN}{stats.received}{Style.RESET_ALL}, "
        f"Lost={Fore.RED}{stats.sent - stats.received}{Style.RESET_ALL} "
        f"({Fore.RED}{stats.packet_loss():.1f}%{Style.RESET_ALL})"
    )
    print_centered(s_line1)

    s_line2 = (
        f"Latency: {Fore.WHITE}Avg={Fore.YELLOW}{stats.avg_latency():.2f}ms{Style.RESET_ALL}, "
        f"Min={Fore.GREEN}{stats.min_latency():.2f}ms{Style.RESET_ALL}, "
        f"Max={Fore.RED}{stats.max_latency():.2f}ms{Style.RESET_ALL}"
    )
    print_centered(s_line2)
    print_centered(f"{Fore.WHITE}{sep}{Style.RESET_ALL}")

async def main():
    clear_screen()
    args = parse_args()

    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    if args.host:
        interval_s = args.interval / 1000.0
        timeout_s  = args.timeout  / 1000.0
        await ping_target(args.host, args.count, interval_s, timeout_s)
        return

    banner = [
        "██████╗ ██╗███╗   ██╗ ██████╗ ███████╗██████╗ ",
        "██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝██╔══██╗",
        "██████╔╝██║██╔██╗ ██║██║  ███╗█████╗  ██████╔╝",
        "██╔═══╝ ██║██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗",
        "██║     ██║██║ ╚████║╚██████╔╝███████╗██║  ██║",
        "╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝"
    ]

    content_h = len(banner) + 6
    top = calc_vertical_margin(content_h)

    print("\n" * top)
    for line in banner:
        print_centered(f"{Fore.WHITE}{line}{Style.RESET_ALL}")

    input_centered(f"{Fore.WHITE}Press [Enter] to start{Style.RESET_ALL}")

    while True:
        host = input_centered(f"{Fore.WHITE}Enter host or IP : {Style.RESET_ALL}")
        if is_valid_ip(host.strip()):
            host = host.strip()
            break
        print_centered(f"{Fore.RED}❌ Invalid host{Style.RESET_ALL}")

    while True:
        c = input_centered(f"{Fore.WHITE}Count [8]: {Style.RESET_ALL}")
        if not c.strip(): count = 8; break
        if c.strip().isdigit() and int(c)>0: count=int(c); break
        print_centered(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}")

    while True:
        i = input_centered(f"{Fore.WHITE}Interval ms [500]: {Style.RESET_ALL}")
        if not i.strip(): interval=500; break
        if i.strip().isdigit() and int(i)>0: interval=int(i); break
        print_centered(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}")

    while True:
        t = input_centered(f"{Fore.WHITE}Timeout ms [1000]: {Style.RESET_ALL}")
        if not t.strip(): timeout=1000; break
        if t.strip().isdigit() and int(t)>0: timeout=int(t); break
        print_centered(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}")

    await ping_target(host, count, interval/1000.0, timeout/1000.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n")
        print_centered(f"{Fore.RED}❌ Interrupted{Style.RESET_ALL}")
        sys.exit(0)
