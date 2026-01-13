#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulk Domain Name Generator
Generate domain variations using regex patterns and creative combinations.
"""

import re
import os
from datetime import datetime
from itertools import product

def generate_from_regex(pattern, max_results=20000):
    """
    Generate strings from a regex pattern.
    
    Args:
        pattern (str): Regex pattern like [a-z]example.com, [a-zA-Z]{2}example.com, or ?example.com
        max_results (int): Maximum number of results to generate
    
    Returns:
        list: List of generated strings
    """
    results = []
    
    # Unescape dots
    pattern_unescaped = pattern.replace(r'\.', '.')
    
    # Handle character classes with quantifiers like [a-zA-Z]{2}
    quantifier_pattern = r'\[([^\]]+)\]\{(\d+)(?:,(\d+))?\}'
    matches = list(re.finditer(quantifier_pattern, pattern))
    
    if matches:
        for match in matches:
            char_class = match.group(1)
            min_count = int(match.group(2))
            max_count = int(match.group(3)) if match.group(3) else min_count
            
            # Parse character ranges
            chars = parse_char_class(char_class)
            
            # Generate combinations for fixed or range quantifiers
            if min_count == max_count:
                count = min_count
                if count <= 3:  # Limit to reasonable combinations
                    for combo in product(chars, repeat=count):
                        combo_str = ''.join(combo)
                        domain = pattern_unescaped.replace(match.group(0), combo_str, 1)
                        results.append(domain)
                        if len(results) >= max_results:
                            return sorted(list(set(results)))
            else:
                # For ranges, generate a few examples
                for count in range(min_count, min(max_count + 1, min_count + 2)):
                    for combo in product(chars, repeat=count):
                        combo_str = ''.join(combo)
                        domain = pattern_unescaped.replace(match.group(0), combo_str, 1)
                        results.append(domain)
                        if len(results) >= max_results:
                            return sorted(list(set(results)))
    
    # Handle character classes [a-z], [0-9], etc. without quantifiers
    elif '[' in pattern and ']' in pattern:
        char_classes = re.findall(r'\[([^\]]+)\]', pattern)
        
        for char_class in char_classes:
            chars = parse_char_class(char_class)
            
            # Generate variations
            base_pattern = re.sub(r'\[[^\]]+\]', '{}', pattern_unescaped, count=1)
            for char in chars[:26]:  # Limit to 26 variations
                domain = base_pattern.format(char)
                results.append(domain)
                if len(results) >= max_results:
                    return sorted(list(set(results)))
    
    # Handle optional characters with ?
    elif '?' in pattern:
        # Example: ?example.com -> example.com, aexample.com, bexample.com, etc.
        base = pattern_unescaped.replace('?', '')
        results.append(base)
        
        # Add single letter variations
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            domain = pattern_unescaped.replace('?', letter)
            results.append(domain)
    
    # Handle + (one or more)
    elif '+' in pattern:
        base = pattern_unescaped.replace('+', '')
        results.append(base)
        
        for i in range(1, 4):
            domain = pattern_unescaped.replace('+', 'a' * i)
            results.append(domain)
    
    # Handle * (zero or more)
    elif '*' in pattern:
        base = pattern_unescaped.replace('*', '')
        results.append(base)
        
        for i in range(1, 3):
            domain = pattern_unescaped.replace('*', 'a' * i)
            results.append(domain)
    
    return sorted(list(set(results)))


def parse_char_class(char_class):
    """
    Parse a character class and return all matching characters.
    
    Args:
        char_class (str): Character class like 'a-z', '0-9', 'a-zA-Z', etc.
    
    Returns:
        list: List of all characters in the class
    """
    chars = []
    i = 0
    while i < len(char_class):
        if i + 2 < len(char_class) and char_class[i + 1] == '-':
            # Range like a-z
            start_char = ord(char_class[i])
            end_char = ord(char_class[i + 2])
            chars.extend([chr(c) for c in range(start_char, end_char + 1)])
            i += 3
        else:
            # Single character
            chars.append(char_class[i])
            i += 1
    return chars


def generate_domain_variations(keyword):
    """
    Generate domain name variations using regex and pattern matching.
    
    Args:
        keyword (str): The domain name part to generate variations for
    
    Returns:
        list: List of generated domain names
    """
    domains = []
    extensions = ['.com', '.io', '.net', '.org', '.co', '.dev', '.app', '.tech']
    
    # Original keyword
    for ext in extensions:
        domains.append(f"{keyword}{ext}")
    
    # Add prefix variations
    prefixes = ['my', 'get', 'the', 'pro', 'super', 'ultra', 'mega', 'smart', 'quick']
    for prefix in prefixes:
        for ext in extensions:
            domains.append(f"{prefix}{keyword}{ext}")
    
    # Add suffix variations
    suffixes = ['hub', 'zone', 'lab', 'pro', 'max', 'plus', 'io', 'app']
    for suffix in suffixes:
        for ext in extensions:
            domains.append(f"{keyword}{suffix}{ext}")
    
    # Number variations
    for num in ['1', '2', '3', '24', '365']:
        for ext in extensions:
            domains.append(f"{keyword}{num}{ext}")
    
    # Vowel variations (common domain hacks)
    vowel_patterns = {
        'a': ['a', '4'],
        'e': ['e', '3'],
        'i': ['i', '1'],
        'o': ['o', '0'],
        'u': ['u']
    }
    
    for original_vowel, variants in vowel_patterns.items():
        for variant in variants:
            modified = keyword.replace(original_vowel, variant)
            if modified != keyword:
                for ext in extensions:
                    domains.append(f"{modified}{ext}")
    
    # Remove duplicates and sort
    domains = sorted(list(set(domains)))
    
    return domains


def validate_regex_pattern(pattern):
    """
    Validate if input is a valid regex pattern.
    
    Args:
        pattern (str): Pattern to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        re.compile(pattern)
        return True, ""
    except re.error as e:
        return False, str(e)


def is_regex_pattern(text):
    """
    Check if text contains regex special characters.
    
    Args:
        text (str): Text to check
    
    Returns:
        bool: True if contains regex patterns
    """
    regex_chars = r'[\[\]?*+{}().|\\^$]'
    return bool(re.search(regex_chars, text))


def main():
    """Main function to run the bulk domain name generator."""
    
    print("=" * 60)
    print("  BULK DOMAIN NAME GENERATOR")
    print("=" * 60)
    print()
    print("You can use:")
    print("  • Simple keywords: tech, app, cloud")
    print("  • Regex patterns: [a-z]example.com, ?example.com, [a-z]{2}example.com, [0-9]app.io")
    print()
    
    # Get user input
    while True:
        user_input = input("Enter a domain name or regex pattern: ").strip().lower()
        
        if not user_input:
            print("❌ Error: Input cannot be empty. Try again.")
            continue
        
        break
    
    print()
    
    # Check if it's a regex pattern
    if is_regex_pattern(user_input):
        print(f"Detected regex pattern: '{user_input}'")
        print("Generating domains from regex pattern...")
        print()
        
        # Validate regex
        is_valid, error_msg = validate_regex_pattern(user_input)
        if not is_valid:
            print(f"❌ Invalid regex pattern: {error_msg}")
            return
        
        domains = generate_from_regex(user_input)
    else:
        # Standard domain variation generation
        print(f"Generating domain variations for: '{user_input}'...")
        print()
        domains = generate_domain_variations(user_input)
    
    if not domains:
        print("❌ No domains generated. Try a different pattern.")
        return
    
    print(f"✓ Generated {len(domains)} domain variations!")
    print()
    
    # Display preview (first 15)
    preview_count = min(15, len(domains))
    print(f"Preview (first {preview_count} domains):")
    print("-" * 40)
    for domain in domains[:preview_count]:
        print(f"  • {domain}")
    if len(domains) > preview_count:
        print(f"  ... and {len(domains) - preview_count} more")
    print()
    
    # Save to file
    filename = "domains.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for domain in domains:
                f.write(f"{domain}\n")
        
        print(f"✓ Successfully saved {len(domains)} domains to '{filename}'")
        print(f"  Location: {os.path.abspath(filename)}")
        
    except IOError as e:
        print(f"❌ Error: Could not write to file. {e}")
        return
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
