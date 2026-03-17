#!/usr/bin/env python3
import asyncio
import os
import socket
import sys
import re
import argparse
import shutil
import datetime
from ping3 import ping
from statistics import mean
from colorama import init, Fore, Style

init(autoreset=True)

W_TRY = 7
W_TGT = 24
W_BYT = 7
W_LAT = 12
W_STS = 8
TABLE_WIDTH = W_TRY + W_TGT + W_BYT + W_LAT + W_STS

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

HELP_TEXT = """Usage:
  pinger HOST [-c COUNT] [-i INTERVAL_MS] [-t TIMEOUT_MS] [-s SIZE] [-o OUTPUT_FILE] [-q]
  pinger -h | --help

Flags:
  HOST                  IP address or hostname to ping
  -c,  --count COUNT    Number of pings to send (0 for infinite, default: 8)
  -i,  --interval MS    Delay between pings in milliseconds (default: 500)
  -t,  --timeout  MS    Timeout per ping in milliseconds (default: 1000)
  -s,  --size BYTES     Payload size in bytes (MTU test, default: 56)
  -o,  --output   FILE  Path to save results as a .txt log file
  -q,  --quiet          Raw output mode (no UI, no colors, no centering)
  -h,  --help           Show this help and exit
"""

def get_term_size():
    return shutil.get_terminal_size((80, 24))

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def print_line(text, quiet=False, align="left"):
    if quiet:
        safe_print(strip_ansi(text))
        return

    clean_len = len(strip_ansi(text))

    if align == "center":
        left_pad = max(0, TABLE_WIDTH - clean_len) // 2
        right_pad = max(0, TABLE_WIDTH - clean_len) - left_pad
        content = " " * left_pad + text + " " * right_pad
    else:
        content = text + " " * max(0, TABLE_WIDTH - clean_len)

    w = get_term_size().columns
    padding = max(0, (w - TABLE_WIDTH) // 2)
    safe_print(" " * padding + content)

def input_centered(prompt):
    clean = strip_ansi(prompt)
    w = get_term_size().columns
    padding = max(0, (w - len(clean)) // 2)
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
    p.add_argument("-s", "--size", type=int, default=56)
    p.add_argument("-o", "--output", type=str, default=None)
    p.add_argument("-q", "--quiet", action="store_true")
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

    def get_jitter(self):
        if len(self.latencies) < 2:
            return 0
        diffs = [abs(self.latencies[i] - self.latencies[i-1]) for i in range(1, len(self.latencies))]
        return mean(diffs)

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

async def ping_target(host, count=8, interval=0.5, timeout=1.0, size=56, output_file=None, quiet=False):
    if not quiet:
        clear_screen()

    stats = PingStats()

    try:
        host = socket.gethostbyname(host)
    except socket.gaierror:
        pass

    total_content_height = 4 + (count if count > 0 else 10) + 5
    top_margin = calc_vertical_margin(total_content_height) if count > 0 else 2

    if not quiet:
        safe_print("\n" * top_margin)

    header_raw = (
        f"{'TRY'.center(W_TRY)}"
        f"{'TARGET'.center(W_TGT)}"
        f"{'BYTES'.center(W_BYT)}"
        f"{'LATENCY'.center(W_LAT)}"
        f"{'STATUS'.center(W_STS)}"
    )
    print_line(f"{Fore.WHITE}{header_raw}{Style.RESET_ALL}", quiet)
    print_line(f"{Fore.WHITE}{'─' * TABLE_WIDTH}{Style.RESET_ALL}", quiet)

    log_f = None
    if output_file:
        try:
            log_f = open(output_file, mode='a', encoding='utf-8')
            start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_f.write(f"{'='*58}\n")
            log_f.write(f"PING SESSION STARTED: {start_time}\n")

            # Formatted compactly to fit inside the new tighter boundary
            log_f.write(f"HOST: {host[:15]:<15} PKT: {size}B INT: {int(interval*1000)}ms TMOUT: {int(timeout*1000)}ms\n")

            log_f.write(f"{'-'*58}\n")
            log_f.write(f"{'TIME':<10} {'SEQ':<6} {'TARGET':<20} {'BYTES':<6} {'LATENCY':<9} {'STATUS'}\n")
            log_f.write(f"{'-'*58}\n")
        except Exception as e:
            print_line(f"{Fore.RED}❌ Failed to open log file: {e}{Style.RESET_ALL}", quiet)
            output_file = None

    i = 0
    interrupted = False
    try:
        while True:
            if count != 0 and i >= count:
                break

            latency = await asyncio.to_thread(ping, host, timeout=timeout, size=size)
            stats.add(latency)

            if latency is None:
                status_txt = "DOWN"
                stat_color = Fore.RED
                lat_disp = "-"
                lat_log = "TIMEOUT"
            else:
                status_txt = "UP"
                stat_color = Fore.GREEN
                lat_ms = latency * 1000
                lat_disp = f"{lat_ms:.2f} ms"
                lat_log = f"{lat_ms:.2f} ms"

            seq_txt = f"#{i+1}"
            host_txt = host if len(host) <= W_TGT-2 else host[:W_TGT-4] + ".."
            byt_txt = str(size)

            raw_c1 = seq_txt.center(W_TRY)
            raw_c2 = host_txt.center(W_TGT)
            raw_c_byt = byt_txt.center(W_BYT)
            raw_c3 = lat_disp.center(W_LAT)
            raw_c4 = status_txt.center(W_STS)

            full_vis = raw_c1 + raw_c2 + raw_c_byt + raw_c3 + raw_c4
            col_c4 = f"{stat_color}{raw_c4}{Style.RESET_ALL}"

            if quiet:
                safe_print(full_vis)
            else:
                w = get_term_size().columns
                pad = max(0, (w - TABLE_WIDTH) // 2)
                safe_print(" " * pad + raw_c1 + raw_c2 + raw_c_byt + raw_c3 + col_c4)

            if log_f:
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                # Fit the log columns nicely into the 58 char limit
                log_f.write(f"{ts:<10} {i+1:<6} {host[:19]:<20} {size:<6} {lat_log:<9} {status_txt}\n")
                log_f.flush()

            i += 1
            await asyncio.sleep(interval)

    except (KeyboardInterrupt, asyncio.CancelledError):
        if not quiet:
            safe_print()
        interrupted = True

    sep = '═' * TABLE_WIDTH
    print_line(f"{Fore.WHITE}{sep}{Style.RESET_ALL}", quiet)

    if interrupted:
        print_line(f"{Fore.YELLOW}⚠️ Ping interrupted by user.{Style.RESET_ALL}", quiet, align="center")

    s_line1 = (
        f"Packets: {Fore.WHITE}Sent={Fore.YELLOW}{stats.sent}{Style.RESET_ALL}, "
        f"Recv={Fore.GREEN}{stats.received}{Style.RESET_ALL}, "
        f"Lost={Fore.RED}{stats.sent - stats.received}{Style.RESET_ALL} "
        f"({Fore.RED}{stats.packet_loss():.1f}%{Style.RESET_ALL})"
    )
    print_line(s_line1, quiet, align="center")

    s_line2 = (
        f"Latency: {Fore.WHITE}Avg={Fore.YELLOW}{stats.avg_latency():.1f}ms{Style.RESET_ALL}, "
        f"Min={Fore.GREEN}{stats.min_latency():.1f}ms{Style.RESET_ALL}, "
        f"Max={Fore.RED}{stats.max_latency():.1f}ms{Style.RESET_ALL}, "
        f"Jitter={Fore.CYAN}{stats.get_jitter():.1f}ms{Style.RESET_ALL}"
    )
    print_line(s_line2, quiet, align="center")

    if output_file:
        abs_path = os.path.abspath(output_file)
        log_msg = f"📄 Log saved to: {Fore.CYAN}{abs_path}{Style.RESET_ALL}"
        print_line(log_msg, quiet, align="center")

    print_line(f"{Fore.WHITE}{sep}{Style.RESET_ALL}", quiet)

    if not quiet:
        safe_print()

    if log_f:
        end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_f.write(f"{'='*58}\n")
        log_f.write(f"SESSION SUMMARY ({end_time})\n")
        log_f.write(f"{'-'*58}\n")
        log_f.write(f"Packets: Sent = {stats.sent}, Received = {stats.received}, Lost = {stats.sent - stats.received} ({stats.packet_loss():.1f}%)\n")
        log_f.write(f"Latency: Min = {stats.min_latency():.2f}ms, Avg = {stats.avg_latency():.2f}ms, Max = {stats.max_latency():.2f}ms, Jitter = {stats.get_jitter():.2f}ms\n")
        log_f.write(f"{'='*58}\n\n")
        log_f.close()

async def main():
    args = parse_args()

    if args.help:
        safe_print(HELP_TEXT)
        sys.exit(0)

    if args.host:
        interval_s = args.interval / 1000.0
        timeout_s  = args.timeout  / 1000.0
        await ping_target(args.host, args.count, interval_s, timeout_s, args.size, args.output, args.quiet)
        return

    if args.quiet and not args.host:
        safe_print("Error: HOST must be provided via arguments when using --quiet mode.")
        sys.exit(1)

    clear_screen()
    banner = [
        "██████╗ ██╗███╗   ██╗ ██████╗ ███████╗██████╗ ",
        "██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝██╔══██╗",
        "██████╔╝██║██╔██╗ ██║██║  ███╗█████╗  ██████╔╝",
        "██╔═══╝ ██║██║╚██╗██║██║   ██║██╔══╝  ██╔══██╗",
        "██║     ██║██║ ╚████║╚██████╔╝███████╗██║  ██║",
        "╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝"
    ]

    content_h = len(banner) + 8
    top = calc_vertical_margin(content_h)

    safe_print("\n" * top)
    for line in banner:
        print_line(f"{Fore.WHITE}{line}{Style.RESET_ALL}", align="center")

    input_centered(f"{Fore.WHITE}Press [Enter] to start{Style.RESET_ALL}")

    while True:
        host = input_centered(f"{Fore.WHITE}Enter host or IP : {Style.RESET_ALL}")
        if is_valid_ip(host.strip()):
            host = host.strip()
            break
        print_line(f"{Fore.RED}❌ Invalid host{Style.RESET_ALL}", align="center")

    while True:
        c = input_centered(f"{Fore.WHITE}Count (0 for infinite) [8]: {Style.RESET_ALL}")
        if not c.strip(): count = 8; break
        if c.strip().isdigit() and int(c)>=0: count=int(c); break
        print_line(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}", align="center")

    while True:
        i = input_centered(f"{Fore.WHITE}Interval ms [500]: {Style.RESET_ALL}")
        if not i.strip(): interval=500; break
        if i.strip().isdigit() and int(i)>0: interval=int(i); break
        print_line(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}", align="center")

    while True:
        t = input_centered(f"{Fore.WHITE}Timeout ms [1000]: {Style.RESET_ALL}")
        if not t.strip(): timeout=1000; break
        if t.strip().isdigit() and int(t)>0: timeout=int(t); break
        print_line(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}", align="center")

    while True:
        s = input_centered(f"{Fore.WHITE}Packet size bytes [56]: {Style.RESET_ALL}")
        if not s.strip(): size = 56; break
        if s.strip().isdigit() and int(s)>0: size=int(s); break
        print_line(f"{Fore.RED}❌ Invalid number{Style.RESET_ALL}", align="center")

    out_file = input_centered(f"{Fore.WHITE}Output .txt file (optional): {Style.RESET_ALL}").strip()
    if not out_file: out_file = None

    await ping_target(host, count, interval/1000.0, timeout/1000.0, size, out_file, quiet=False)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        safe_print("\n")
        print_line(f"{Fore.YELLOW}Script exited.{Style.RESET_ALL}", align="center")
        sys.exit(0)
    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
