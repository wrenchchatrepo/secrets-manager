"""
Keychain Module

This module provides functions for securely storing and retrieving
credentials from the macOS Keychain.
"""

import subprocess
from typing import Dict, Optional, Any, List, Union

# Service name for the keychain entries
SERVICE_NAME = "mcp-servers"

# Organization details keys
ORG_KEYS = [
    "COMPANY_OWNER_SSN",
    "BANK_ACCT",
    "BANK_ROUTING",
    "COMPANY_NAME",
    "COMPANY_EIN",
    "COMPANY_ADDRESS",
    "COMPANY_OWNER"
]

def get_from_keychain(service: str, account: str) -> Optional[str]:
    """
    Retrieve a password from the macOS Keychain.
    
    Args:
        service: The service name
        account: The account/key name
        
    Returns:
        str: The retrieved password/value, or None if not found
    """
    try:
        cmd = ["security", "find-generic-password", "-s", service, "-a", account, "-w"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # Item not found or other error - return None silently
            return None
    except Exception as e:
        print(f"❌ Error retrieving {account}: {str(e)}")
        return None

def store_in_keychain(service: str, account: str, password: str) -> bool:
    """
    Store a password in the macOS Keychain.
    
    Args:
        service: The service name
        account: The account/key name
        password: The password/value to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Delete any existing password for this service and account
        subprocess.run(
            ["security", "delete-generic-password", "-s", service, "-a", account],
            stderr=subprocess.DEVNULL,
            check=False,
        )
        
        # Add the new password
        subprocess.run(
            ["security", "add-generic-password", "-s", service, "-a", account, "-w", password],
            check=True,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False

def get_organization_details() -> Dict[str, str]:
    """
    Retrieve all organization details from the Keychain.
    
    Returns:
        Dict[str, str]: Dictionary of organization details
    """
    details = {}
    for key in ORG_KEYS:
        value = get_from_keychain(SERVICE_NAME, key)
        if value:
            details[key] = value
    return details

def get_specific_detail(key: str) -> Optional[str]:
    """
    Retrieve a specific organization detail from the Keychain.
    
    Args:
        key: The key to retrieve
        
    Returns:
        Optional[str]: The value, or None if not found
    """
    if key not in ORG_KEYS:
        print(f"❌ Unknown key: {key}")
        print(f"Available keys: {', '.join(ORG_KEYS)}")
        return None
    
    return get_from_keychain(SERVICE_NAME, key) 