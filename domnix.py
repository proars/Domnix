#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Domnix - Fast Bulk Domain Availability Checker
Multi-threaded WHOIS CLI for checking domain registration status.
"""

import argparse
import concurrent.futures as cf
import csv
import http.client
import os
import re
import socket
import sys
import time
import shutil
import threading
from typing import Optional, List

# Global flag for stopping process
STOP_REQUESTED = False

# Phrases that indicate domain is available/not registered
AVAILABLE_MARKERS = [
    "no match", "not found", "no entries found", "no data found",
    "status: available", "status: free", "domain not found", "no object found",
    "no such domain", "not registered", "object does not exist",
    "no records", "no data available"
]

# Simple cache to avoid querying IANA too often
WHOIS_SERVER_CACHE = {}
USER_AGENT = "Domnix/0.1"
WHOIS_OVERRIDES = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "io": "whois.nic.io",
    "co": "whois.nic.co",
    "ai": "whois.ai",
    "gg": "whois.gg",
    "je": "whois.je",
    "me": "whois.nic.me",
    "app": "whois.nic.google",
    "dev": "whois.nic.google",
    "xyz": "whois.nic.xyz",
    "ru": "whois.tcinet.ru",
    "su": "whois.tcinet.ru",
}
USE_COLOR = sys.stdout.isatty()

def color(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def style_status(status: str) -> str:
    mapping = {
        "free": ("free", "32"),
        "registered": ("registered", "31"),
        "unknown": ("unknown", "33"),
        "error": ("error", "35"),
        "invalid": ("invalid", "90"),
    }
    label, code = mapping.get(status, (status, "0"))
    return color(label, code)

def resolve_dns(domain: str, timeout: float = 3.0) -> str:
    """Resolve A/AAAA records and return a short summary."""
    try:
        res = socket.getaddrinfo(domain, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
    except Exception as e:
        return f"dns error: {e}"[:80]
    v4, v6 = [], []
    for family, _type, _proto, _canon, sockaddr in res:
        ip = sockaddr[0]
        if family == socket.AF_INET:
            v4.append(ip)
        elif family == socket.AF_INET6:
            v6.append(ip)
    parts = []
    if v4:
        parts.append("A: " + ",".join(sorted(set(v4))[:3]))
    if v6:
        parts.append("AAAA: " + ",".join(sorted(set(v6))[:3]))
    return " | ".join(parts) if parts else "dns: no data"

def probe_http(domain: str, timeout: float = 4.0) -> str:
    """Do a quick HEAD on https then http, return status summary."""
    hosts = [("https", 443, http.client.HTTPSConnection), ("http", 80, http.client.HTTPConnection)]
    last_err = None
    for scheme, port, cls in hosts:
        try:
            conn = cls(domain, port=port, timeout=timeout)
            conn.request("HEAD", "/", headers={"User-Agent": USER_AGENT})
            resp = conn.getresponse()
            conn.close()
            return f"{scheme} {resp.status}"
        except Exception as e:
            last_err = e
    return f"http error: {last_err}"[:80]

def to_ascii(domain: str) -> str:
    """Converts IDN to punycode (example: 'bücher.de' -> 'xn--bcher-kva.de')."""
    domain = domain.strip().strip(".").lower()
    if not domain:
        return domain
    try:
        return domain.encode("idna").decode("ascii")
    except Exception:
        return domain

def is_valid_domain(domain: str) -> bool:
    """Strict ASCII domain validation after IDNA conversion.
    - total length <= 253
    - at least two labels
    - each label 1..63, allowed [a-z0-9-]
    - label must start/end with [a-z0-9]
    """
    if not domain or len(domain) > 253:
        return False
    if "." not in domain:
        return False
    labels = domain.split(".")
    if len(labels) < 2:
        return False
    for lbl in labels:
        if not (1 <= len(lbl) <= 63):
            return False
        if not re.fullmatch(r"[a-z0-9-]+", lbl):
            return False
        if not (lbl[0].isalnum() and lbl[-1].isalnum()):
            return False
    return True

def whois_query(server: str, query: str, timeout: float = 6.0) -> str:
    """Sends a query to whois server (port 43) and returns raw response."""
    with socket.create_connection((server, 43), timeout=timeout) as s:
        s.sendall((query + "\r\n").encode("utf-8", errors="ignore"))
        s.shutdown(socket.SHUT_WR)
        chunks = []
        while True:
            data = s.recv(4096)
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks).decode("utf-8", errors="ignore", )

def find_whois_server(domain: str, timeout: float = 6.0, override: Optional[str] = None) -> Optional[str]:
    """Find whois server via override, cache, IANA, or whois-servers.net pattern."""
    # Get TLD (last label)
    parts = domain.split(".")
    if len(parts) < 2:
        return None
    tld = parts[-1]

    if override:
        return override

    if tld in WHOIS_SERVER_CACHE:
        return WHOIS_SERVER_CACHE[tld]

    if tld in WHOIS_OVERRIDES:
        WHOIS_SERVER_CACHE[tld] = WHOIS_OVERRIDES[tld]
        return WHOIS_OVERRIDES[tld]

    try:
        resp = whois_query("whois.iana.org", tld, timeout=timeout)
    except Exception:
        resp = ""
    m = re.search(r"whois:\s*(\S+)", resp, flags=re.IGNORECASE)
    if m:
        server = m.group(1).strip()
        WHOIS_SERVER_CACHE[tld] = server
        return server

    # Fallback to whois-servers.net pattern for many gTLDs
    fallback = f"{tld}.whois-servers.net"
    WHOIS_SERVER_CACHE[tld] = fallback
    return fallback

def interpret_whois(raw: str) -> str:
    """Basic heuristic: determines if domain is registered/available/unknown."""
    text = raw.lower()
    if any(marker in text for marker in AVAILABLE_MARKERS):
        return "free"
    # Many registries contain indicators of existing domain
    if re.search(r"^domain name:\s*\S+", raw, re.IGNORECASE | re.MULTILINE):
        return "registered"
    if re.search(r"^status:\s*(ok|client|server|active|registered)", raw,
                 re.IGNORECASE | re.MULTILINE):
        return "registered"
    # If profile and contacts are found - likely registered
    if re.search(r"registrant|registry expiry date|created:", raw, re.IGNORECASE):
        return "registered"
    return "unknown"

def check_one(
    domain: str,
    timeout: float = 6.0,
    retry: int = 1,
    default_tld: str = "com",
    do_dns: bool = False,
    do_http: bool = False,
    dns_timeout: float = 3.0,
    http_timeout: float = 4.0,
    whois_server_override: Optional[str] = None,
) -> dict:
    """Checks one domain and optional DNS/HTTP. Returns a result dict."""
    # Add default TLD if no TLD specified
    if "." not in domain:
        domain = domain + f".{default_tld}"
        
    d = to_ascii(domain)
    if not d or not is_valid_domain(d):
        return {"domain": domain, "status": "invalid", "note": "Invalid domain name", "dns": "", "http": ""}
    server = find_whois_server(d, timeout=timeout, override=whois_server_override)
    if not server:
        return {"domain": domain, "status": "unknown", "note": "WHOIS server not found", "dns": "", "http": ""}
    # Some registries require "domain example.com" format
    queries = [d, f"domain {d}"]
    last_err = None
    dns_info = resolve_dns(d, dns_timeout) if do_dns else ""
    http_info = probe_http(d, http_timeout) if do_http else ""

    for attempt in range(retry + 1):
        for q in queries:
            try:
                raw = whois_query(server, q, timeout=timeout)
                status = interpret_whois(raw)
                if status != "unknown":
                    return {"domain": domain, "status": status, "note": f"whois: {server}", "dns": dns_info, "http": http_info}
            except Exception as e:
                last_err = str(e)
                time.sleep(0.2)

    if last_err:
        return {"domain": domain, "status": "error", "note": last_err, "dns": dns_info, "http": http_info}
    return {"domain": domain, "status": "unknown", "note": f"whois: {server}", "dns": dns_info, "http": http_info}

def keyboard_listener():
    """Listen for 'q' key press to stop the process."""
    global STOP_REQUESTED
    try:
        while not STOP_REQUESTED:
            if sys.platform == "win32":
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == 'q':
                        STOP_REQUESTED = True
                        print("\n\n" + color("⚠ Stop requested! Finishing current checks and saving...", "33"))
                        break
            else:
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'q':
                        STOP_REQUESTED = True
                        print("\n\n" + color("⚠ Stop requested! Finishing current checks and saving...", "33"))
                        break
            time.sleep(0.1)
    except Exception:
        pass  # Silently fail if keyboard input not available

def save_remaining_domains(domains: List[str], output_path: str):
    """Save remaining unchecked domains to file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(domains))
        return True
    except Exception as e:
        print(f"Error saving domains: {e}", file=sys.stderr)
        return False

def load_domains(path: str) -> List[str]:
    domains = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        # First try to split by commas
        if "," in content:
            # Handle comma-separated format
            domains = [d.strip() for d in content.split(",")]
        else:
            # Handle line-by-line format
            domains = [line.strip() for line in content.splitlines()]
    
    # Filter out empty lines and comments
    domains = [d for d in domains if d and not d.startswith("#") and not d.startswith("=")]
    
    # Remove numbering like "1. domain.com" or "  123. domain.com"
    cleaned_domains = []
    for d in domains:
        # Remove leading numbers and dots (e.g., "123. domain.com" -> "domain.com")
        d = re.sub(r'^\s*\d+\.\s*', '', d).strip()
        if d:
            cleaned_domains.append(d)
    
    return cleaned_domains

def main():
    parser = argparse.ArgumentParser(description="Check domain registration status using WHOIS")
    parser.add_argument("input", nargs="?", help="File with domain list (comma-separated or one per line)")
    parser.add_argument("--out", help="CSV file to save results (default: print to stdout)")
    parser.add_argument("--tld", help="Default TLD to add if domain has no extension (default: com)")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers (default: 10)")
    parser.add_argument("--timeout", type=float, default=6.0, help="WHOIS query timeout in seconds")
    parser.add_argument("--dns", action="store_true", help="Resolve DNS (A/AAAA) for each domain")
    parser.add_argument("--http", action="store_true", help="Probe HTTP/HTTPS status via HEAD request")
    parser.add_argument("--dns-timeout", type=float, default=3.0, help="DNS resolution timeout (default: 3.0)")
    parser.add_argument("--http-timeout", type=float, default=4.0, help="HTTP probe timeout (default: 4.0)")
    parser.add_argument("--whois-server", help="Override WHOIS server (applies to all domains in this run)")
    args = parser.parse_args()

    # Interactive mode when no input provided
    input_path = args.input
    domains = []
    
    if not input_path:
        # Check if domains.txt exists
        if os.path.exists("domains.txt"):
            print(color("📋 Found domains.txt in current directory", "36"))
            response = input(color("Use this file? (Y/n): ", "33")).strip().lower()
            if response in ["", "y", "yes"]:
                input_path = "domains.txt"
            else:
                input_path = None
        
        # If no file selected, offer interactive input
        if not input_path:
            print(color("\n🔍 Domnix - Domain Availability Checker", "36;1"))
            print(color("─" * 45, "90"))
            print("\nChoose an option:")
            print(color("  1)", "33"), "Enter domains manually (comma-separated)")
            print(color("  2)", "33"), "Specify a file path")
            print(color("  3)", "33"), "Exit")
            
            choice = input(color("\nYour choice (1-3): ", "33")).strip()
            
            if choice == "1":
                print(color("\n💡 Tip:", "36"), "Enter domains separated by commas or spaces")
                print(color("   Example:", "90"), "example.com, mysite.net, test.org")
                domain_input = input(color("\nEnter domains: ", "33")).strip()
                
                if not domain_input:
                    print(color("❌ No domains entered. Exiting.", "31"), file=sys.stderr)
                    sys.exit(1)
                
                # Parse input (handle both comma and space separation)
                if "," in domain_input:
                    domains = [d.strip() for d in domain_input.split(",")]
                else:
                    domains = [d.strip() for d in domain_input.split()]
                
                domains = [d for d in domains if d]
                
                if not domains:
                    print(color("❌ No valid domains found. Exiting.", "31"), file=sys.stderr)
                    sys.exit(1)
                    
            elif choice == "2":
                file_path = input(color("Enter file path: ", "33")).strip()
                if not file_path or not os.path.exists(file_path):
                    print(color(f"❌ File not found: {file_path}", "31"), file=sys.stderr)
                    sys.exit(1)
                input_path = file_path
            else:
                print(color("👋 Goodbye!", "36"))
                sys.exit(0)
    
    # Load domains from file if path is set
    if input_path:
        try:
            domains = load_domains(input_path)
        except FileNotFoundError:
            print(color(f"❌ File not found: {input_path}", "31"), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(color(f"❌ Error reading file: {e}", "31"), file=sys.stderr)
            sys.exit(1)
    
    if not domains:
        print(color("❌ No valid domains to check. Exiting.", "31"), file=sys.stderr)
        sys.exit(1)
    
    # Show what we're about to check
    print(color(f"\n✓ Loaded {len(domains)} domain(s) to check", "32"))

    results = []
    # Get default TLD (default to "com" if not specified)
    default_tld = args.tld if args.tld else "com"
    
    total_domains = len(domains)
    completed = 0
    checked_domains = set()
    
    # Start keyboard listener thread
    global STOP_REQUESTED
    STOP_REQUESTED = False
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()
    
    print(f"Starting check for {total_domains} domains...")
    print(color("Press 'q' at any time to stop and save remaining domains.", "36"))
    print()
    
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [
            ex.submit(
                check_one,
                d,
                args.timeout,
                default_tld=default_tld,
                do_dns=args.dns,
                do_http=args.http,
                dns_timeout=args.dns_timeout,
                http_timeout=args.http_timeout,
                whois_server_override=args.whois_server,
            )
            for d in domains
        ]
        for fut in cf.as_completed(futs):
            if STOP_REQUESTED:
                # Cancel remaining futures
                for f in futs:
                    f.cancel()
                break
                
            result = fut.result()
            results.append(result)
            checked_domains.add(result.get('domain', ''))
            completed += 1
            
            # Show progress
            percentage = (completed / total_domains) * 100
            bar_length = 40
            filled = int(bar_length * completed / total_domains)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Status counter for current batch
            status_emoji = {
                'free': '✓',
                'registered': '✗',
                'unknown': '?',
                'error': '!',
                'invalid': '⨯'
            }
            emoji = status_emoji.get(result.get('status', ''), '•')
            
            print(f"\r[{bar}] {percentage:5.1f}% ({completed}/{total_domains}) {emoji} {result.get('domain', '')[:40]:<40}", end='', flush=True)
    
    print("\n")  # New line after progress bar
    
    # Save remaining domains if stopped early
    if STOP_REQUESTED:
        remaining = [d for d in domains if d not in checked_domains]
        if remaining and input_path:
            if save_remaining_domains(remaining, input_path):
                print(color(f"✓ Saved {len(remaining)} unchecked domains back to {input_path}", "32"))
            else:
                print(color(f"✗ Failed to save remaining domains", "31"), file=sys.stderr)
        elif remaining and not input_path:
            print(color(f"⚠ {len(remaining)} domains were not checked (manual entry mode)", "33"))
        print(color(f"Stopped after checking {completed}/{total_domains} domains.", "33"))
        print()

    # Preserve the original input order
    order = {d: i for i, d in enumerate(domains)}
    results.sort(key=lambda r: order.get(r["domain"], 10**9))

    # Always print to console first (table only)
    term_width = shutil.get_terminal_size((120, 40)).columns
    col_domain = 32
    col_status = 10
    col_note = 22
    col_dns = 22
    col_http = max(12, term_width - (col_domain + col_status + col_note + col_dns + 10))

    def trunc(text: str, width: int) -> str:
        return text if len(text) <= width else text[: max(0, width - 1)] + "…"

    header = f"{ 'DOMAIN':{col_domain}}  {'STATUS':{col_status}}  {'NOTE':{col_note}}  {'DNS':{col_dns}}  HTTP"
    print(header)
    print("-" * min(term_width, len(header) + col_http))

    counts = {"free": 0, "registered": 0, "unknown": 0, "error": 0, "invalid": 0}

    for row in results:
        d = trunc(row.get("domain", ""), col_domain)
        s = row.get("status", "")
        note = trunc(row.get("note", ""), col_note)
        dns_info = trunc(row.get("dns", ""), col_dns)
        http_info = trunc(row.get("http", ""), col_http)
        counts[s] = counts.get(s, 0) + 1
        print(f"{d:{col_domain}}  {style_status(s):{col_status}}  {note:{col_note}}  {dns_info:{col_dns}}  {http_info}")

    total = sum(counts.values())
    print("-" * min(term_width, len(header) + col_http))
    summary = "  ".join([
        f"free: {counts['free']}",
        f"registered: {counts['registered']}",
        f"unknown: {counts['unknown']}",
        f"error: {counts['error']}",
        f"invalid: {counts['invalid']}",
        f"total: {total}",
    ])
    print(summary)

    # Save output after executing (CSV only)
    csv_path = args.out or "results.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["domain", "status", "note", "dns", "http"])
        for row in results:
            w.writerow([
                row.get("domain", ""),
                row.get("status", ""),
                row.get("note", ""),
                row.get("dns", ""),
                row.get("http", ""),
            ])

    print(f"\nOutput saved: CSV -> {csv_path}")

if __name__ == "__main__":
    main()
