#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import concurrent.futures as cf
import csv
import re
import socket
import sys
import time
from typing import Tuple, Optional, List




# Phrases that indicate domain is available/not registered
AVAILABLE_MARKERS = [
    "no match", "not found", "no entries found", "no data found",
    "status: available", "status: free", "domain not found", "no object found",
    "no such domain", "not registered", "object does not exist"
]
# Add non-English variants that also indicate availability
AVAILABLE_MARKERS += ["не найден", "свободен", "нет данных"]

# Simple cache to avoid querying IANA too often
WHOIS_SERVER_CACHE = {}

def to_ascii(domain: str) -> str:
    """Converts IDN to punycode (example: 'пример.рф' -> 'xn--e1afmkfd.xn--p1ai')."""
    domain = domain.strip().strip(".").lower()
    if not domain:
        return domain
    try:
        return domain.encode("idna").decode("ascii")
    except Exception:
        return domain

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

def find_whois_server(domain: str, timeout: float = 6.0) -> Optional[str]:
    """Queries IANA to find the appropriate whois server for the domain zone."""
    # Get TLD (last label)
    parts = domain.split(".")
    if len(parts) < 2:
        return None
    tld = parts[-1]
    if tld in WHOIS_SERVER_CACHE:
        return WHOIS_SERVER_CACHE[tld]
    try:
        resp = whois_query("whois.iana.org", tld, timeout=timeout)
    except Exception:
        return None
    m = re.search(r"whois:\s*(\S+)", resp, flags=re.IGNORECASE)
    if m:
        server = m.group(1).strip()
        WHOIS_SERVER_CACHE[tld] = server
        return server
    return None

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

def check_one(domain: str, timeout: float = 6.0, retry: int = 1, default_tld: str = "com") -> Tuple[str, str, str]:
    """Checks one domain. Returns (domain, status, note)."""
    # Add default TLD if no TLD specified
    if "." not in domain:
        domain = domain + f".{default_tld}"
        
    d = to_ascii(domain)
    if not d or "." not in d:
        return (domain, "invalid", "Invalid domain name")
    server = find_whois_server(d, timeout=timeout)
    if not server:
        return (domain, "unknown", "WHOIS server not found at IANA")
    # Some registries require "domain example.com" format
    queries = [d, f"domain {d}"]
    last_err = None
    for attempt in range(retry + 1):
        for q in queries:
            try:
                raw = whois_query(server, q, timeout=timeout)
                status = interpret_whois(raw)
                if status != "unknown":
                    return (domain, status, f"whois: {server}")
                # Если неизвестно — всё равно вернем unknown с сервером
                return (domain, "unknown", f"whois: {server}")
            except Exception as e:
                last_err = str(e)
                time.sleep(0.2)
    return (domain, "error", f"{last_err or 'Ошибка WHOIS-запроса'}")

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
    domains = [d for d in domains if d and not d.startswith("#")]
    return domains

def main():
    parser = argparse.ArgumentParser(description="Check domain registration status using WHOIS")
    parser.add_argument("input", help="File with domain list (comma-separated or one per line)")
    parser.add_argument("--out", help="CSV file to save results (default: print to stdout)")
    parser.add_argument("--tld", help="Default TLD to add if domain has no extension (default: com)")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers (default: 10)")
    parser.add_argument("--timeout", type=float, default=6.0, help="WHOIS query timeout in seconds")
    args = parser.parse_args()

    domains = load_domains(args.input)
    if not domains:
        print("File is empty or contains no valid domains.", file=sys.stderr)
        sys.exit(1)

    results = []
    # Get default TLD (default to "com" if not specified)
    default_tld = args.tld if args.tld else "com"
    
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(check_one, d, args.timeout, default_tld=default_tld) for d in domains]
        for fut in cf.as_completed(futs):
            results.append(fut.result())

    # Сортируем как в исходном списке
    order = {d: i for i, d in enumerate(domains)}
    results.sort(key=lambda r: order.get(r[0], 10**9))

    # Always print to console first
    print(f"{'DOMAIN':40}  {'STATUS':12}  NOTE")
    for d, s, note in results:
        status_display = f"{s:12}"
        print(f"{d:40}  {status_display}  {note}")

    # Save to CSV if output file specified
    if args.out:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["domain", "status", "note"])
            w.writerows(results)
        print(f"\nResults saved to: {args.out}")

if __name__ == "__main__":
    main()
