"""
Command Line Interface

This module provides CLI functionality for managing credentials.
"""

import argparse
import getpass
import sys
import os
import re
from typing import Dict, List, Optional

from .keychain import (
    get_from_keychain,
    store_in_keychain,
    get_organization_details,
    get_specific_detail,
    SERVICE_NAME,
    ORG_KEYS
)

def mask_sensitive_value(key: str, value: str) -> str:
    """Mask sensitive information for display."""
    if any(sensitive in key for sensitive in ['SSN', 'EIN', 'BANK', 'ACCT', 'ROUTING']):
        if len(value) > 4:
            return '*' * (len(value) - 4) + value[-4:]
        else:
            return '*' * len(value)
    return value

def parse_credentials_file(file_path: str) -> Dict[str, str]:
    """Parse a file containing credentials in the format KEY = "VALUE"."""
    credentials = {}
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all key-value pairs in the format KEY = "VALUE" or KEY = 'VALUE'
    pattern = r'([A-Z_]+)\s*=\s*["\']([^"\']*)["\']'
    matches = re.findall(pattern, content)
    
    for key, value in matches:
        if key in ORG_KEYS:
            credentials[key] = value
    
    return credentials

def list_credentials():
    """List all credentials stored in the keychain."""
    print(f"=== Organization Credentials in Keychain ===")
    print(f"Service name: {SERVICE_NAME}")
    print()
    
    found_any = False
    
    for key in ORG_KEYS:
        value = get_from_keychain(SERVICE_NAME, key)
        
        if value is None:
            continue
            
        display_value = mask_sensitive_value(key, value)
        print(f"{key}: {display_value}")
        found_any = True
    
    if not found_any:
        print("No organization credentials found.")
        print("Run 'mcp-credentials store' to add organization details to the Keychain.")
    
    print()
    print("For more information, run: mcp-credentials --help")

def store_credential(key: str, value: str = None):
    """Store a single credential in the keychain."""
    if key not in ORG_KEYS:
        print(f"Error: Unknown key '{key}'")
        print(f"Available keys: {', '.join(ORG_KEYS)}")
        sys.exit(1)
    
    if value is None:
        # Prompt for the value with masked input if sensitive
        is_sensitive = any(sensitive in key for sensitive in ['SSN', 'EIN', 'BANK', 'ACCT', 'ROUTING'])
        if is_sensitive:
            value = getpass.getpass(f"Enter value for {key}: ")
        else:
            value = input(f"Enter value for {key}: ")
    
    if not value:
        print("Error: Value cannot be empty.")
        sys.exit(1)
    
    # Store the credential
    if store_in_keychain(SERVICE_NAME, key, value):
        print(f"Successfully stored {key} in Keychain.")
    else:
        print(f"Failed to store {key} in Keychain.")
        sys.exit(1)

def store_credentials_from_file(file_path: str, yes: bool = False):
    """Store credentials from a file."""
    print(f"=== Store Organization Credentials from File ===")
    print(f"Service name: {SERVICE_NAME}")
    print(f"File: {file_path}")
    print()
    
    # Parse the credentials file
    credentials = parse_credentials_file(file_path)
    
    if not credentials:
        print("No valid credentials found in the file.")
        print(f"Available credential keys: {', '.join(ORG_KEYS)}")
        sys.exit(1)
    
    print(f"Found {len(credentials)} credentials to store:")
    for key, value in credentials.items():
        display_value = mask_sensitive_value(key, value)
        print(f"  - {key}: {display_value}")
    
    # Confirm before proceeding
    if not yes:
        confirm = input("\nDo you want to store these credentials? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Store the credentials
    success = True
    for key, value in credentials.items():
        print(f"Storing {key}...")
        if not store_in_keychain(SERVICE_NAME, key, value):
            print(f"Failed to store {key}.")
            success = False
    
    if success:
        print("\n✅ All credentials have been stored in the Keychain.")
    else:
        print("\n⚠️ Some credentials could not be stored.")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="MCP Credentials - Secure Credential Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all stored credentials")
    
    # Store command
    store_parser = subparsers.add_parser("store", help="Store a credential")
    store_parser.add_argument("key", choices=ORG_KEYS, help="The credential key to store")
    store_parser.add_argument("--value", help="The value to store (will prompt if not provided)")
    
    # Store-file command
    store_file_parser = subparsers.add_parser("store-file", help="Store credentials from a file")
    store_file_parser.add_argument("file", help="Path to the credentials file")
    store_file_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a stored credential")
    get_parser.add_argument("key", choices=ORG_KEYS, help="The credential key to retrieve")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "list":
        list_credentials()
    elif args.command == "store":
        store_credential(args.key, args.value)
    elif args.command == "store-file":
        store_credentials_from_file(args.file, args.yes)
    elif args.command == "get":
        value = get_specific_detail(args.key)
        if value:
            print(value)
        else:
            print(f"No value found for {args.key}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 