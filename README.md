# Domnix 🔍 – Fast Bulk Domain Availability Checker + Generator

[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A powerful domain toolkit featuring a **bulk WHOIS checker** and **regex-based domain generator**. Check domain availability with multi-threaded WHOIS queries, generate creative domain variations with regex patterns, and export results to CSV. Perfect for domain hunters, startup founders, brand protection teams, and developers.

## ✨ Key Features

- 🎯 **Interactive Mode** - User-friendly prompts with manual domain entry or file selection
- ⚡ **Multi-threaded WHOIS** - Check hundreds of domains simultaneously  
- 🛑 **Graceful Stop (Press 'q')** - Stop anytime and resume later  
- 🎨 **Regex Domain Generator** - Create domain variations with patterns  
- 📊 **Real-time Progress** - Live progress bar with status indicators  
- 🌐 **IDN Support** - International domain names with punycode  
- 📁 **CSV Export** - Auto-save results after execution  
- 🎨 **Colorized Output** - Beautiful terminal UI with status colors

---

## 🌟 Overview

Domnix includes two powerful tools:

1. **Domain Checker** (`domnix.py`) - Check domain availability with fast WHOIS queries
2. **Domain Generator** (`bulk_domain_generator.py`) - Generate domain variations using regex patterns

### 🎯 Perfect for

- 🚀 Startup founders searching for the perfect domain
- 💼 Domain investors performing bulk availability checks
- 🛡️ Brand managers monitoring domain variations
- 👨‍💻 Developers building domain-related tools
- 📈 SEO specialists looking for brandable domains

---

## 📦 Tool #1: Domain Availability Checker

Fast multi-threaded WHOIS checker with interactive mode and real-time progress tracking.

### ✨ Features

*   🎯 **Interactive Mode** - User-friendly prompts when starting without arguments
*   ⌨️ **Manual Entry** - Enter domains directly (comma or space-separated)
*   📁 **File Support** - Load from file or auto-detect `domains.txt`
*   ⚡ **Multi-threaded** - Check hundreds of domains simultaneously
*   🛑 **Graceful Stop (Press 'q')** - Stop anytime, auto-save unchecked domains
*   📊 **Real-time Progress Bar** - Visual progress with percentage and status emojis
*   🌐 **IDN Support** - International domain names with punycode conversion
*   🔍 **DNS & HTTP Probes** - Optional A/AAAA resolution and HTTP status checks
*   💾 **CSV Export** - Results saved automatically after execution
*   🚀 **Smart Caching** - WHOIS server caching for faster results
*   🎨 **Colorized Output** - Status indicators and summary statistics

### 🚀 Quick Start

**Interactive mode (no arguments):**

```bash
python domnix.py
```

You'll see:
```
🔍 Domnix - Domain Availability Checker
─────────────────────────────────────────────

Choose an option:
  1) Enter domains manually (comma-separated)
  2) Specify a file path
  3) Exit

Your choice (1-3): 
```

**Option 1 - Manual entry:**
```bash
💡 Tip: Enter domains separated by commas or spaces
   Example: example.com, mysite.net, test.org

Enter domains: google.com, facebook.com, myapp.dev
```

**Option 2 - File input:**

Create `domains.txt`:
```
example1.com
example2.com
example3.net
```

Then run:
```bash
python domnix.py
# or
python domnix.py mydomains.txt
```

### 📋 Command Line Options

| Option | Default | Description |
| --- | --- | --- |
| `input` | Interactive/`domains.txt` | File containing domain list or interactive mode |
| `--out` | `results.csv` | CSV file to save results |
| `--tld` | `com` | Default TLD to add if domain has no extension |
| `--workers` | `10` | Number of parallel workers (1-50 recommended) |
| `--timeout` | `6.0` | WHOIS query timeout in seconds |
| `--dns` | `False` | Resolve A/AAAA records for each domain |
| `--http` | `False` | Probe HTTP/HTTPS with HEAD request |
| `--dns-timeout` | `3.0` | DNS resolution timeout |
| `--http-timeout` | `4.0` | HTTP probe timeout |
| `--whois-server` | `auto` | Override WHOIS server for all domains |

### 💡 Usage Examples

**Basic check with default settings:**
```bash
python domnix.py domains.txt
```

**Check with DNS and HTTP probes:**
```bash
python domnix.py domains.txt --dns --http
```

**High-speed checking (more workers):**
```bash
python domnix.py domains.txt --workers 50 --timeout 10
```

**Custom TLD and output:**
```bash
python domnix.py mylist.txt --tld net --out availability.csv
```

**Check specific domains quickly:**
```bash
python domnix.py
# Choose option 1, enter: startup.com, myapp.io, techco.dev
```

### 📊 Progress Indicator

During execution, you'll see a live progress bar:

```
✓ Loaded 500 domain(s) to check
Starting check for 500 domains...
Press 'q' at any time to stop and save remaining domains.

[████████████████░░░░░░░░░░░░] 45.2% (226/500) ✓ example-domain.com
```

**Status Emojis:**

| Emoji | Status | Meaning |
|-------|--------|---------|
| ✓ | `free` | Domain is available for registration |
| ✗ | `registered` | Domain is already taken |
| ? | `unknown` | Could not determine status |
| ! | `error` | Error occurred while checking |
| ⨯ | `invalid` | Invalid domain name format |

### 🛑 Stop Process Anytime

**Press 'q' at any time during execution:**

*   ✅ Finishes checking currently running domains
*   💾 Saves all checked results to CSV
*   📝 Saves remaining unchecked domains back to input file
*   🔄 Resume later by running again with same file

**Example:**

```
Starting check for 1000 domains...
Press 'q' at any time to stop and save remaining domains.

[████████████░░░░░░░░░░░░░░░░] 30.5% (305/1000) ✓ example-domain.com
[User presses 'q']

⚠ Stop requested! Finishing current checks and saving...

✓ Saved 695 unchecked domains back to domains.txt
Stopped after checking 305/1000 domains.

DOMAIN                            STATUS        NOTE
example1.com                      free          whois: whois.verisign-grs.com
example2.com                      registered    whois: whois.verisign-grs.com
...
----------------------------------------------------------------
free: 120  registered: 150  unknown: 25  error: 8  invalid: 2  total: 305

Output saved: CSV -> results.csv
```

### 📈 Output Format

**Console Output:**

```
✓ Loaded 500 domain(s) to check
Starting check for 500 domains...
Press 'q' at any time to stop and save remaining domains.

[████████████████████████████████████████] 100.0% (500/500) ✓ lastdomain.com

DOMAIN                            STATUS        NOTE                      DNS                       HTTP
example.com                       registered    whois: whois.verisign...  A: 93.184.216.34         https 200
mydomain.com                      free          whois: whois.verisign...                          
test123.net                       free          whois: whois.verisign...                          
invalid-..domain.com              invalid       Invalid domain name                               
------------------------------------------------------------------------------------------------------
free: 245  registered: 230  unknown: 15  error: 5  invalid: 5  total: 500

Output saved: CSV -> results.csv
```

**CSV Output (`results.csv`):**

```csv
domain,status,note,dns,http
example.com,registered,whois: whois.verisign-grs.com,A: 93.184.216.34,https 200
mydomain.com,free,whois: whois.verisign-grs.com,,
test123.net,free,whois: whois.verisign-grs.com,,
invalid-..domain.com,invalid,Invalid domain name,,
```

### 📝 Domain List Formats

**Supported formats:**

**1. Line-by-line:**
```
example1.com
example2.com
example3.net
```

**2. Comma-separated:**
```
example1.com, example2.com, example3.net
```

**3. With comments (ignored):**
```
# My domain list
example1.com
example2.com  # This is a comment

# Another section
example3.net
```

**4. Manual entry (interactive mode):**
```
example.com, test.io, myapp.dev
```
or
```
example.com test.io myapp.dev
```

---

## 📦 Tool #2: Bulk Domain Generator

Generate hundreds of domain variations using regex patterns and creative combinations.

### ✨ Features

*   🎯 **Regex Pattern Support** - Use patterns like `[a-z]example.com` or `[a-z]{2}press.com`
*   🔤 **Character Classes** - Support for `[a-z]`, `[0-9]`, `[a-zA-Z]`, custom sets
*   📏 **Quantifiers** - `{2}`, `{1,3}`, `?`, `+`, `*` for flexible patterns
*   🎨 **Auto-Variations** - Prefixes, suffixes, numbers, vowel replacements
*   📝 **Clean Output** - Plain text format ready for domnix.py

### 🚀 Usage

Run the generator:

```bash
python bulk_domain_generator.py
```

Then enter a pattern:

**Simple keyword:**
```
tech
```
Generates: `tech.com`, `mytech.com`, `techlab.com`, `tech365.com`, etc.

**Regex patterns:**
```
[a-z]press.com           # apress.com, bpress.com, ..., zpress.com
[a-z]{2}example.com      # aaexample.com, abexample.com, ..., zzexample.com
?example.com             # example.com, aexample.com, bexample.com, ...
[0-9]app.io              # 0app.io, 1app.io, ..., 9app.io
```

### 📋 Pattern Examples

| Pattern | Description | Example Results |
| --- | --- | --- |
| `[a-z]press.com` | Single letter prefix | apress.com, bpress.com, zpress.com |
| `[a-z]{2}tech.com` | Two letter combinations | aatech.com, abtech.com, zztech.com |
| `[0-9]{3}app.io` | Three digit combinations | 000app.io, 001app.io, 999app.io |
| `?domain.com` | Optional character | domain.com, adomain.com, bdomain.com |
| `tech` | Keyword variations | tech.com, mytech.io, techlab.net |

### 📁 Output

Generates `domains.txt` with clean domain list:

```
apress.com
bpress.com
cpress.com
...
```

---

## 🔄 Complete Workflow Example

**Step 1: Generate domain variations**

```bash
python bulk_domain_generator.py
# Enter: [a-z]{2}press.com
# Output: 676 domains saved to domains.txt
```

**Step 2: Check availability**

```bash
python domnix.py domains.txt --workers 20
# Progress bar shows real-time status
# Results saved to results.csv
```

**Step 3: Find available domains**

```bash
# Windows PowerShell:
Select-String -Pattern ",free," results.csv

# Linux/Mac:
grep ",free," results.csv

# Get count of available domains:
(Select-String -Pattern ",free," results.csv).Count
```

**Step 4: Export available domains**

```bash
# PowerShell
Get-Content results.csv | Select-String ",free," | ForEach-Object { ($_ -split ',')[0] } | Out-File available-domains.txt

# Bash/Linux
grep ",free," results.csv | cut -d',' -f1 > available-domains.txt
```

---

## 🔧 Installation

**Requirements:**

*   Python 3.6 or higher  
*   No external dependencies (uses only Python standard library)

**Quick Start:**

```bash
# Clone the repository
git clone https://github.com/proars/domnix.git
cd domnix

# Run the domain checker (interactive mode)
python domnix.py

# Or run the domain generator
python bulk_domain_generator.py
```

**Manual Installation:**

1. Download the repository as ZIP
2. Extract to your desired location
3. Open terminal in the extracted folder
4. Run: `python domnix.py`

---

## 📝 Implementation Details

**Domain Checker (`domnix.py`):**

*   ✅ Built with pure Python, no external WHOIS libraries required
*   ⚡ Uses `concurrent.futures` for efficient parallel processing
*   🧠 Implements smart WHOIS server caching for faster results
*   🌐 Supports IDN (Internationalized Domain Names)
*   🛡️ Handles rate limiting and connection timeouts gracefully
*   🎯 Built-in WHOIS server overrides + IANA discovery with fallback
*   ⌨️ Cross-platform keyboard input handling for graceful stopping
*   🎨 ANSI color support with fallback for non-color terminals

**Domain Generator (`bulk_domain_generator.py`):**

*   🔍 Regex-based pattern matching using Python's `re` module
*   🔤 Support for character classes, quantifiers, and complex patterns
*   🧮 Smart character class parser for ranges (a-z, 0-9, A-Z)
*   🔄 Generates combinations using `itertools.product`
*   🎯 Automatic deduplication and sorting
*   📊 Limits output to prevent excessive combinations (configurable)

---

## 🔧 Technical Notes

### Domain Checker

*   **Graceful interruption**: Press 'q' during execution to stop gracefully - unchecked domains are saved back to the input file for later resume
*   **Auto TLD**: Automatically appends TLD if not specified (default: .com)
*   **Smart parsing**: Intelligent parsing of WHOIS responses across different registrars
*   **Comment support**: Lines starting with `#` are ignored in domain lists
*   **IDN support**: Full Unicode/IDN support for international domains
*   **Progress bar**: Real-time updates using ANSI escape codes
*   **Cross-platform**: Works on Windows, Linux, and macOS
*   **Keyboard handling**: Uses `msvcrt` on Windows, `select` on Unix-like systems

### Domain Generator

*   **Escaped dots**: Handles `\.com` notation correctly
*   **Max results**: Default limit of 20,000 combinations (configurable)
*   **Deduplication**: Automatically removes duplicate domains
*   **Sorting**: Results are sorted alphabetically
*   **Format validation**: Basic domain format checking before output

---

## 💡 Advanced Examples

**1. Generate premium 2-letter domains:**

```bash
python bulk_domain_generator.py
# Enter: [a-z]{2}.com
# Generates: aa.com, ab.com, ..., zz.com (676 domains)
```

**2. Check with high concurrency:**

```bash
python domnix.py domains.txt --workers 50 --timeout 10
```

**3. Check with full DNS and HTTP analysis:**

```bash
python domnix.py domains.txt --dns --http --dns-timeout 5 --http-timeout 6
```

**4. Generate domains with numbers:**

```bash
python bulk_domain_generator.py
# Enter: [a-z][0-9]{2}app.com
# Generates: a00app.com, a01app.com, ..., z99app.com (2,600 domains)
```

**5. Quick check of specific domains:**

```bash
python domnix.py
# Choose option 1
# Enter: startup.io, myapp.dev, techco.com, brandname.co
```

**6. Resume interrupted check:**

```bash
python domnix.py domains.txt
# Press 'q' after 50%
# Later: python domnix.py domains.txt  (continues with remaining domains)
```

---

## 🐛 Troubleshooting

### Generator Issues

**"No domains generated":**
*   ✅ Ensure your regex pattern is valid
*   ✅ Check that quantifiers aren't generating too many combinations (>20,000 default limit)
*   ✅ Try simpler patterns first: `[a-z]domain.com`
*   ✅ Use proper escape sequences: `example\.com` or just `example.com`

### Checker Issues

**"Unknown status" responses:**
*   ✅ Some registries limit WHOIS queries or use non-standard responses
*   ✅ Try increasing `--timeout` value (e.g., `--timeout 10`)
*   ✅ Use `--whois-server` to specify alternative WHOIS server
*   ✅ Re-run later if you suspect rate limiting
*   ✅ Reduce `--workers` count (try 5-10 instead of 50)

**"Invalid domain name" errors:**
*   ✅ Domains must contain valid characters: `a-z`, `0-9`, hyphens only
*   ✅ Domains must have at least two labels: `example.com` (not just `example`)
*   ✅ Labels cannot start or end with hyphens
*   ✅ Total domain length must be ≤253 characters
*   ✅ Each label must be ≤63 characters

**Progress bar not displaying correctly:**
*   ✅ Ensure you're using a modern terminal (PowerShell, Windows Terminal, or modern Unix terminal)
*   ✅ Old CMD on Windows may not support ANSI colors
*   ✅ Terminal must support ANSI escape codes

**Keyboard stop ('q') not working:**
*   ✅ On Windows: Use PowerShell or Windows Terminal (not old CMD)
*   ✅ On Unix: Ensure terminal is in proper input mode
*   ✅ Try pressing 'q' multiple times if needed
*   ✅ Check terminal has focus and is not in selection mode

**Rate limiting / Connection timeouts:**
*   ✅ Reduce number of parallel workers: `--workers 5`
*   ✅ Increase timeout values: `--timeout 10`
*   ✅ Add delays between batch runs
*   ✅ Some registries have strict rate limits - check their policies

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1.  Fork the repository
2.  Create your feature branch: `git checkout -b feature/amazing-feature`
3.  Commit your changes: `git commit -m 'Add amazing feature'`
4.  Push to the branch: `git push origin feature/amazing-feature`
5.  Open a Pull Request

**Ideas for contributions:**

*   Additional regex pattern support and generators
*   More domain variation algorithms (phonetic, semantic)
*   Support for additional WHOIS servers and TLDs
*   Performance optimizations and caching improvements
*   Better error handling and retry mechanisms
*   Additional output formats (JSON, XML, HTML reports)
*   GUI interface option
*   Docker containerization
*   API endpoints for web integration

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

*   [IANA](https://www.iana.org/) for providing WHOIS server information
*   The Python community for inspiration and excellent standard library
*   All contributors who help improve this tool
*   Domain hunters and startup founders who provided feedback

---

## 📊 Project Stats

- **Pure Python** - No external dependencies required
- **Cross-platform** - Windows, Linux, macOS support
- **Fast** - Multi-threaded checking (10+ workers default)
- **Lightweight** - Under 600 lines of code total
- **Open Source** - MIT License

---

## 📞 Support

- 📧 Report issues on [GitHub Issues](https://github.com/proars/domnix/issues)
- 💬 Questions? Open a [Discussion](https://github.com/proars/domnix/discussions)
- 🌐 Visit [ARS Tech](https://arstech.net) for more tools

---

## 🔖 Keywords

domain availability checker, bulk WHOIS, domain name generator, regex domain patterns, IDN support, multi-threaded WHOIS, DNS resolution, HTTP status check, CSV export, cross-platform, open source domain checker, domain availability tool, domain lookup, fast WHOIS, parallel WHOIS, command-line domain checker, CLI domain tool, domain hunter, brandable domains, domain variations, startup domain finder, domain search tool, batch domain checker, Python domain tool

---

**Made with ❤️ by [ARS Tech](https://arstech.net)**