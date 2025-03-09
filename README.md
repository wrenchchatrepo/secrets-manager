# Secrets Manager

A secure credential management system for macOS. This package provides tools to securely store and retrieve credentials using the macOS Keychain.

## Features

- **Secure Storage**: Store sensitive credentials in the macOS Keychain
- **Command Line Interface**: Manage credentials from the command line
- **REST API Server**: Access credentials via a secure REST API
- **Python Library**: Integrate credential management into your Python applications

## Installation

```bash
# Clone the repository
git clone https://github.com/wrenchchatrepo/secrets-manager.git
cd secrets-manager

# Install the package
pip install -e .
```

## Command Line Usage

### List All Credentials

```bash
secrets-manager list
```

### Store a Credential

```bash
secrets-manager store COMPANY_NAME
# You will be prompted to enter the value
```

Or specify the value directly:

```bash
secrets-manager store COMPANY_NAME --value "Example Company LLC"
```

### Retrieve a Credential

```bash
secrets-manager get COMPANY_NAME
```

### Store Credentials from a File

Create a file with your credentials in the format:

```
COMPANY_NAME = "Example Company LLC"
COMPANY_EIN = "12-3456789"
```

Then run:

```bash
secrets-manager store-file credentials.txt
```

## API Server

The package includes a REST API server for managing credentials over HTTP.

### Starting the Server

```bash
secrets-manager-server --host localhost --port 8000
```

The server generates a temporary API key if none is provided. To specify your own API key:

```bash
secrets-manager-server --api-key your-api-key
```

Or set it as an environment variable:

```bash
export SECRETS_MANAGER_API_KEY=your-api-key
secrets-manager-server
```

### API Endpoints

All endpoints require authentication using the API key in the `Authorization` header:

```
Authorization: Bearer your-api-key
```

#### List All Credentials

```
GET /credentials
```

Response:

```json
{
  "service": "mcp-servers",
  "credentials": {
    "COMPANY_NAME": "Example Company LLC",
    "COMPANY_EIN": "******789"
  },
  "available_keys": ["COMPANY_NAME", "COMPANY_EIN", ...]
}
```

#### Get a Specific Credential

```
GET /credentials/COMPANY_NAME
```

Response:

```json
{
  "key": "COMPANY_NAME",
  "value": "Example Company LLC",
  "masked_value": "Example Company LLC"
}
```

#### Store a Credential

```
POST /credentials/COMPANY_NAME
Content-Type: application/json

{
  "value": "Example Company LLC"
}
```

Response:

```json
{
  "message": "Successfully stored COMPANY_NAME in Keychain",
  "key": "COMPANY_NAME",
  "masked_value": "Example Company LLC"
}
```

## Python Library Usage

### Import the Library

```python
from secrets_manager import get_specific_detail, store_in_keychain, SERVICE_NAME
```

### Retrieve a Credential

```python
company_name = get_specific_detail("COMPANY_NAME")
print(f"Company: {company_name}")
```

### Store a Credential

```python
store_in_keychain(SERVICE_NAME, "COMPANY_NAME", "Example Company LLC")
```

## Available Credential Keys

The following credential keys are available by default:

- `COMPANY_OWNER_SSN`: Social Security Number of the company owner
- `BANK_ACCT`: Bank account number
- `BANK_ROUTING`: Bank routing number
- `COMPANY_NAME`: Legal name of the company
- `COMPANY_EIN`: Employer Identification Number
- `COMPANY_ADDRESS`: Company's physical address
- `COMPANY_OWNER`: Name of the company owner

## Security Notes

1. The command-line tools and API server should be run in a secure environment.
2. Never commit sensitive information to version control.
3. The macOS Keychain provides strong encryption for your credentials.
4. Access to the Keychain may require user authentication depending on your macOS security settings.
5. The REST API server uses API key authentication. Keep your API key secure.

## Extending the System

To add additional credential types, modify the `ORG_KEYS` list in `secrets_manager/keychain.py`. 