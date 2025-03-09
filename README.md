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

The package includes a REST API server for managing credentials over HTTP, secured with API key authentication.

### Starting the Server

```bash
secrets-manager-server --host localhost --port 8000
```

### API Key Authentication

The server requires API key authentication for all requests. There are three ways to provide the API key:

#### 1. Command-line Argument

Specify the API key when starting the server:

```bash
secrets-manager-server --api-key your-api-key
```

#### 2. Environment Variable

Set the API key as an environment variable before starting the server:

```bash
export SECRETS_MANAGER_API_KEY=your-api-key
secrets-manager-server
```

#### 3. Auto-generated Key

If no API key is provided, the server generates a temporary key that's valid for just that server instance:

```
⚠️ No API key provided or found in environment.
⚠️ Generated temporary API key: a1b2c3d4e5f6...
⚠️ This key will be valid only for this server instance.
```

### Making Authenticated API Requests

All API requests must include the API key in the `Authorization` header:

```
Authorization: Bearer your-api-key
```

Example using curl:

```bash
# List all credentials
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/credentials

# Get a specific credential
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/credentials/COMPANY_NAME

# Store a credential
curl -X POST \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"value": "Example Company LLC"}' \
  http://localhost:8000/credentials/COMPANY_NAME
```

Example using Python requests:

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# List all credentials
response = requests.get(f"{BASE_URL}/credentials", headers=HEADERS)
credentials = response.json()

# Get a specific credential
response = requests.get(f"{BASE_URL}/credentials/COMPANY_NAME", headers=HEADERS)
credential = response.json()

# Store a credential
data = {"value": "Example Company LLC"}
response = requests.post(f"{BASE_URL}/credentials/COMPANY_NAME", 
                        headers={**HEADERS, "Content-Type": "application/json"}, 
                        json=data)
result = response.json()
```

### API Endpoints

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

### Docker Deployment

The included Dockerfile supports API key configuration:

```bash
# Build the Docker image
docker build -t secrets-manager .

# Run with an API key
docker run -p 8000:8000 -e SECRETS_MANAGER_API_KEY=your-api-key secrets-manager

# Or with a mounted volume for persistence
docker run -p 8000:8000 \
  -e SECRETS_MANAGER_API_KEY=your-api-key \
  -v /path/to/keychain:/app/keychain \
  secrets-manager
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
6. Always use HTTPS in production to encrypt all API traffic.
7. Rotate API keys periodically and immediately after any suspected compromise.

## Extending the System

To add additional credential types, modify the `ORG_KEYS` list in `secrets_manager/keychain.py`.
