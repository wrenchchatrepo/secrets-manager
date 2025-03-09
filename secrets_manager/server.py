"""
REST API Server

This module provides a REST API server for managing credentials.
"""

import os
import json
import argparse
import hashlib
import hmac
import time
from typing import Dict, List, Union, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .keychain import (
    get_from_keychain,
    store_in_keychain,
    get_organization_details,
    get_specific_detail,
    SERVICE_NAME,
    ORG_KEYS
)

class CredentialServer:
    def __init__(self, host: str = "localhost", port: int = 8000, api_key: str = None):
        """Initialize the credential server."""
        self.host = host
        self.port = port
        self.api_key = api_key or os.environ.get("SECRETS_MANAGER_API_KEY")
        
        if not self.api_key:
            self.api_key = self._generate_api_key()
            print(f"⚠️ No API key provided or found in environment.")
            print(f"⚠️ Generated temporary API key: {self.api_key}")
            print(f"⚠️ This key will be valid only for this server instance.")
        
        self.server = None
    
    def _generate_api_key(self) -> str:
        """Generate a temporary API key."""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()
    
    def start(self):
        """Start the credential server."""
        handler = self._create_request_handler()
        self.server = HTTPServer((self.host, self.port), handler)
        
        print(f"Starting Secrets Manager server on http://{self.host}:{self.port}")
        print(f"API endpoints:")
        print(f"  GET  /credentials       - List all credentials")
        print(f"  GET  /credentials/:key  - Get a specific credential")
        print(f"  POST /credentials/:key  - Store a credential")
        print(f"Press Ctrl+C to stop the server.")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            self.server.server_close()
    
    def _create_request_handler(self):
        """Create a request handler class with access to the server instance."""
        api_key = self.api_key
        
        class CredentialRequestHandler(BaseHTTPRequestHandler):
            def _validate_api_key(self) -> bool:
                """Validate the API key from the request headers."""
                auth_header = self.headers.get("Authorization", "")
                
                if not auth_header.startswith("Bearer "):
                    return False
                
                request_api_key = auth_header[7:]  # Remove "Bearer " prefix
                return hmac.compare_digest(api_key, request_api_key)
            
            def _send_response_json(self, data: Dict, status: int = 200):
                """Send a JSON response."""
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            
            def _send_error_json(self, error: str, status: int = 400):
                """Send an error response."""
                self._send_response_json({"error": error}, status)
            
            def _get_json_body(self) -> Dict:
                """Get the JSON body from the request."""
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length == 0:
                    return {}
                
                body = self.rfile.read(content_length).decode()
                return json.loads(body)
            
            def _parse_url(self) -> Dict:
                """Parse the URL to extract path and query parameters."""
                url = urlparse(self.path)
                path = url.path.strip("/").split("/")
                query = parse_qs(url.query)
                
                return {
                    "path": path,
                    "query": query
                }
            
            def _mask_sensitive_value(self, key: str, value: str) -> str:
                """Mask sensitive information for display."""
                if any(sensitive in key for sensitive in ['SSN', 'EIN', 'BANK', 'ACCT', 'ROUTING']):
                    if len(value) > 4:
                        return '*' * (len(value) - 4) + value[-4:]
                    else:
                        return '*' * len(value)
                return value
            
            def do_GET(self):
                """Handle GET requests."""
                if not self._validate_api_key():
                    self._send_error_json("Invalid API key", 401)
                    return
                
                url_data = self._parse_url()
                path = url_data["path"]
                
                if len(path) == 1 and path[0] == "credentials":
                    # List all credentials
                    details = get_organization_details()
                    
                    # Mask sensitive values
                    masked_details = {}
                    for key, value in details.items():
                        masked_details[key] = self._mask_sensitive_value(key, value)
                    
                    self._send_response_json({
                        "service": SERVICE_NAME,
                        "credentials": masked_details,
                        "available_keys": ORG_KEYS
                    })
                
                elif len(path) == 2 and path[0] == "credentials":
                    # Get a specific credential
                    key = path[1]
                    
                    if key not in ORG_KEYS:
                        self._send_error_json(f"Unknown key: {key}", 404)
                        return
                    
                    value = get_specific_detail(key)
                    
                    if value is None:
                        self._send_error_json(f"No value found for key: {key}", 404)
                        return
                    
                    self._send_response_json({
                        "key": key,
                        "value": value,
                        "masked_value": self._mask_sensitive_value(key, value)
                    })
                
                else:
                    # Unknown endpoint
                    self._send_error_json("Unknown endpoint", 404)
            
            def do_POST(self):
                """Handle POST requests."""
                if not self._validate_api_key():
                    self._send_error_json("Invalid API key", 401)
                    return
                
                url_data = self._parse_url()
                path = url_data["path"]
                
                if len(path) == 2 and path[0] == "credentials":
                    # Store a credential
                    key = path[1]
                    
                    if key not in ORG_KEYS:
                        self._send_error_json(f"Unknown key: {key}", 400)
                        return
                    
                    try:
                        body = self._get_json_body()
                    except json.JSONDecodeError:
                        self._send_error_json("Invalid JSON body", 400)
                        return
                    
                    if "value" not in body:
                        self._send_error_json("Missing required field: value", 400)
                        return
                    
                    value = body["value"]
                    
                    if not value:
                        self._send_error_json("Value cannot be empty", 400)
                        return
                    
                    # Store the credential
                    if store_in_keychain(SERVICE_NAME, key, value):
                        self._send_response_json({
                            "message": f"Successfully stored {key} in Keychain",
                            "key": key,
                            "masked_value": self._mask_sensitive_value(key, value)
                        })
                    else:
                        self._send_error_json(f"Failed to store {key} in Keychain", 500)
                
                else:
                    # Unknown endpoint
                    self._send_error_json("Unknown endpoint", 404)
            
            def log_message(self, format, *args):
                """Override log_message to print with timestamp."""
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {self.address_string()} - {format % args}")
        
        return CredentialRequestHandler

def main():
    """Main entry point for the server."""
    parser = argparse.ArgumentParser(description="Secrets Manager Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--api-key", help="API key for authentication (will be generated if not provided)")
    
    args = parser.parse_args()
    
    server = CredentialServer(args.host, args.port, args.api_key)
    server.start()

if __name__ == "__main__":
    main() 