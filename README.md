# Domnix 🔍 – Fast Bulk Domain Availability Checker (WHOIS CLI)

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A lightning-fast, multi-threaded WHOIS CLI for bulk domain availability checking. Includes DNS resolution and HTTP status probes, IDN (internationalized domain name) support, and automatic CSV outputs after executing. Ideal for domain hunters, startup founders, brand protection teams, and developers building domain tools.

## SEO Keywords

Bulk domain availability checker, WHOIS CLI, domain name search, IDN support, multi-threaded WHOIS, DNS resolution, HTTP status check, CSV export, cross-platform, open source domain checker, domain availability tool, domain lookup, fast WHOIS, parallel WHOIS, command-line domain checker.

## 🌟 Overview

Domnix is a powerful command-line tool that helps you:
- Check domain availability across multiple TLDs (.com, .net, .org, etc.)
- Process hundreds of domain names simultaneously
- Support international domain names (IDN)
- Get instant results with parallel processing
- Export findings to CSV for further analysis

### 🎯 Perfect for:
- Startup founders searching for the perfect domain
- Domain investors performing bulk availability checks
- Brand managers monitoring domain availability
- Developers building domain-related tools

## ✨ Key Features

- Check multiple domains at once
- Supports both comma-separated and line-by-line domain lists
- Automatically adds .com if no TLD is specified
- Shows results on screen and optionally saves to CSV
- Handles international domain names (IDN)
- Parallel processing for faster results
- Optional DNS resolution (A/AAAA)
- Optional HTTP/HTTPS HEAD status probes
- Table output plus CSV export
- Strict domain validation (RFC-like rules) to avoid malformed queries
 - Colorized status and end-of-run summary in terminal

## Usage

1. Create a text file with your domain names (e.g., `domains.txt`). You can list domains in two ways:

   Comma-separated:
   ```
   example1, example2, example3
   ```

   Or one per line:
   ```
   example1
   example2
   example3
   ```

2. Run the script (defaults to `domains.txt` if you omit the argument):
   ```
   # uses domains.txt automatically if present
   python domnix.py

   # or specify a file explicitly
   python domnix.py domains.txt
   ```

   To save results to a CSV file:
   ```
   python domnix.py domains.txt --out results.csv
   ```

   To include DNS and HTTP probes:
    ```
    python domnix.py domains.txt --dns --http
    ```

### Outputs after executing

- By default, results are saved to `results.csv` in the working directory.
- If you pass `--out myfile.csv`, CSV is saved to `myfile.csv`.

## Command Line Options

- `input`: File containing domain list (optional; defaults to domains.txt when omitted and present)
- `--out`: CSV file to save results (optional)
- `--tld`: Default TLD to add if domain has no extension (default: com)
- `--workers`: Number of parallel workers (default: 10)
- `--timeout`: WHOIS query timeout in seconds (default: 6.0)
- `--dns`: Resolve A/AAAA records for each domain
- `--http`: Probe HTTP/HTTPS with a HEAD request and report status
- `--dns-timeout`: DNS resolution timeout (default: 3.0)
- `--http-timeout`: HTTP probe timeout (default: 4.0)
- (Table output only; CSV is saved after execution)
- `--whois-server`: Override WHOIS server for all domains (useful for gTLDs or rate limits)

### TLD Examples

Check domains with .com (default):
```
python domnix.py domains.txt
```

Check domains with .net:
```
python domnix.py domains.txt --tld net
```

Check domains with .org:
```
python domnix.py domains.txt --tld org
```

## Output Status

The tool will show one of these statuses for each domain:
- `free`: Domain is available for registration
- `registered`: Domain is already taken
- `unknown`: Could not determine status
- `error`: Error occurred while checking
- `invalid`: Invalid domain name format

## Example Output

```
DOMAIN                                    STATUS        NOTE
example.com                              registered    whois: whois.verisign-grs.com
mydomain.com                             free          whois: whois.verisign-grs.com
```

## 📝 Implementation Details

- Built with pure Python, no external WHOIS libraries required
- Uses concurrent.futures for efficient parallel processing
- Implements smart WHOIS server caching for faster results
- Supports IDN (Internationalized Domain Names)
- Handles rate limiting and connection timeouts gracefully
- Built-in WHOIS server overrides + IANA discovery with fallback

## 🔧 Technical Notes

- Automatically appends TLD if not specified (default: .com)
- Intelligent parsing of WHOIS responses across different registrars
- Comments in domain lists (lines starting with #) are ignored
- Empty lines are automatically filtered
- Full Unicode/IDN support for international domains
 
## Troubleshooting

- Unknown status: Some registries limit WHOIS or use non-standard responses. Try increasing `--timeout`, adding `--whois-server`, or re-running later.
- Private/multi-level zones: For domains like `*.co.uk`, discovery uses `.uk` WHOIS; override with `--whois-server` if needed.
- Rate limits: Reduce `--workers` or add small delays between runs to avoid throttling.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=proars/domnix&type=Date)](https://star-history.com/#proars/domnix&Date)

## 🙏 Acknowledgments

- IANA for providing WHOIS server information
- The Python community for inspiration and support
- All contributors who help improve this tool

---
Made with ❤️ by | [Website](https://arstech.net) 
