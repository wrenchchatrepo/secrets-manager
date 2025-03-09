"""
Secrets Manager - Secure Credential Management System

A package for securely managing organization credentials using macOS Keychain.
"""

__version__ = '0.1.0'

from .keychain import (
    get_from_keychain,
    store_in_keychain,
    get_specific_detail,
    get_organization_details,
    SERVICE_NAME,
    ORG_KEYS
)

__all__ = [
    'get_from_keychain',
    'store_in_keychain',
    'get_specific_detail',
    'get_organization_details',
    'SERVICE_NAME',
    'ORG_KEYS'
] 