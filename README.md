# Domnix 🔍 - Fast Domain Name Availability Checker

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A lightning-fast, multi-threaded Python tool for bulk domain availability checking using WHOIS servers. Perfect for domain hunters, startup founders, and brand protection teams.

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

2. Run the script:
   ```
   python domnix.py domains.txt
   ```

   To save results to a CSV file:
   ```
   python domnix.py domains.txt --out results.csv
   ```

## Command Line Options

- `input`: File containing domain list (required)
- `--out`: CSV file to save results (optional)
- `--tld`: Default TLD to add if domain has no extension (default: com)
- `--workers`: Number of parallel workers (default: 10)
- `--timeout`: WHOIS query timeout in seconds (default: 6.0)

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

## 🔧 Technical Notes

- Automatically appends TLD if not specified (default: .com)
- Intelligent parsing of WHOIS responses across different registrars
- Comments in domain lists (lines starting with #) are ignored
- Empty lines are automatically filtered
- Full Unicode/IDN support for international domains

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

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/domnix&type=Date)](https://star-history.com/#YOUR_USERNAME/domnix&Date)

## 🔗 Related Projects

- [PyWhois](https://github.com/richardpenman/pywhois) - Python WHOIS module
- [python-whois](https://github.com/DannyCork/python-whois) - Another WHOIS implementation
- [domain-tools](https://github.com/topics/domain-tools) - More domain-related tools

## 🙏 Acknowledgments

- IANA for providing WHOIS server information
- The Python community for inspiration and support
- All contributors who help improve this tool

---
Made with ❤️ by | [Website](https://arstech.net.com) 
