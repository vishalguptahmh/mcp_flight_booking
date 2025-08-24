# OAuth 2.0 Authentication Architecture

**Author:** Vishal Gupta  
**System:** VG_FLIGHTMCP_2024

## How OAuth Works with VG Flight Booking

### Architecture Overview

The system supports two modes of operation:

1. **MCP Tools** (Claude Desktop Integration)
   - Direct integration with Claude Desktop
   - No authentication required for Claude Desktop compatibility
   - Uses MCP protocol over stdio
   - Best for conversational interface

2. **HTTP REST APIs** (OAuth Protected)
   - Programmatic access for external applications  
   - OAuth 2.0 JWT tokens required
   - Standard HTTP/JSON APIs
   - Best for mobile apps, web apps, other services

### OAuth Flow

When OAuth is enabled, the system follows this flow:

```
Client App → OAuth Server → API Server
     |            |             |
     | 1. Request Token         |
     |----------->|             |
     |            |             |
     | 2. JWT Token             |
     |<-----------|             |
     |            |             |
     | 3. API Call + Token      |
     |------------------------->|
     |            |             |
     |            | 4. Validate |
     |            |<------------|
     |            |             |
     | 5. API Response          |
     |<-------------------------|
```

## OAuth Server Configuration

### Starting the OAuth Server

```bash
# Start OAuth server on port 9000
cd flight_booking_mcp
.venv/bin/python -m flight_booking_mcp.auth.oauth_server
```

### Client Credentials

The system includes pre-configured clients:

- **Claude Desktop**: `claude-desktop-client` / `claude-desktop-secret`
- **MCP Client**: `mcp-client` / `mcp-client-secret`  
- **VS Code**: `vscode-mcp-client` / `vscode-mcp-secret`

### Token Request

```bash
POST http://localhost:9000/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=claude-desktop-client
&client_secret=claude-desktop-secret
&scope=read write
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer", 
  "expires_in": 3600,
  "scope": "read write"
}
```

## API Usage

### Making Authenticated Requests

When OAuth is enabled, include the Bearer token in requests:

```bash
Authorization: Bearer <access_token>
```

### Token Validation

The MCP server validates tokens by:

1. Checking JWT signature
2. Verifying token expiration
3. Validating issuer and audience
4. Confirming client credentials

## Configuration Options

### Without OAuth (Default)

```json
{
  "env": {
    "OAUTH_ENABLED": "false"
  }
}
```

### With OAuth

```json
{
  "env": {
    "OAUTH_ENABLED": "true",
    "OAUTH_SERVER_URL": "http://localhost:9000",
    "CLIENT_ID": "claude-desktop-client",
    "CLIENT_SECRET": "claude-desktop-secret"
  }
}
```

## Security Features

- **JWT Tokens**: Industry standard token format
- **Token Expiration**: 1-hour token lifetime
- **Client Validation**: Only registered clients can authenticate
- **Scope-based Access**: Read/write permissions
- **Secure Secrets**: Configurable client secrets

## Troubleshooting

### Common Issues

1. **"Invalid client"** - Check client_id and client_secret match configuration
2. **"Token expired"** - Request a new token
3. **"Unauthorized"** - Ensure Bearer token is included in request headers
4. **Connection refused** - Verify OAuth server is running on correct port

### Debug Mode

Enable debug logging to see detailed OAuth flow:

```bash
export LOG_LEVEL=DEBUG
.venv/bin/python -m flight_booking_mcp.auth.oauth_server
```
```bash
POST http://localhost:9000/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=mcp-client-vg
&client_secret=vg-secret-key-2024
&scope=read write
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

### Step 2: Use Token for API Calls
```bash
GET http://localhost:8000/mcp/airports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔧 Running the OAuth Demo

### Option 1: Complete Demo Script
```bash
cd /path/to/flight_booking_mcp
python demo_oauth_complete.py
```

This will:
1. Start OAuth server (port 9000)
2. Start MCP server (port 8000)
3. Demonstrate client authentication
4. Make authenticated API calls
5. Show token validation

### Option 2: Manual Setup

#### Terminal 1: Start OAuth Server
```bash
cd /path/to/flight_booking_mcp
python -c "from src.flight_booking_mcp.auth.oauth_server import run_oauth_server; run_oauth_server()"
```

#### Terminal 2: Start API Server
```bash
cd /path/to/flight_booking_mcp
python -c "from src.flight_booking_mcp.authenticated_api import run_authenticated_api_server; run_authenticated_api_server()"
```

#### Terminal 3: Test Client
```bash
cd /path/to/flight_booking_mcp
python oauth_client_demo.py
```

## 🔐 Security Features

### JWT Token Structure
```json
{
  "sub": "demo-user",
  "client_id": "mcp-client-vg", 
  "scope": "read write",
  "exp": 1640995200,
  "iat": 1640991600,
  "iss": "VG_OAUTH_SERVER",
  "aud": "VG_MCP_CLIENT"
}
```

### Token Validation
- **Signature Verification:** HS256 algorithm with secret key
- **Expiration Check:** Tokens expire after 1 hour
- **Audience Validation:** Must match expected client
- **Issuer Validation:** Must be from VG OAuth server

### Security Headers
```http
Authorization: Bearer <jwt_token>
User-Agent: VG-FlightClient/1.0
Content-Type: application/json
```

## 📋 API Endpoints

### OAuth Server (Port 9000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/oauth/token` | POST | Get access token |
| `/oauth/authorize` | GET | Authorization code flow |
| `/` | GET | Server info |

### MCP Server (Port 8000)
| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | ❌ | API information |
| `/mcp/airports` | GET | ✅ | List airports |
| `/mcp/search-flights` | POST | ✅ | Search flights |
| `/mcp/create-booking` | POST | ✅ | Create booking |
| `/mcp/bookings` | GET | ✅ | Get user bookings |

## 🧪 Testing Authentication

### Valid Token Request
```bash
curl -X POST http://localhost:9000/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=mcp-client-vg&client_secret=vg-secret-key-2024&scope=read write"
```

### Authenticated API Call
```bash
curl -X GET "http://localhost:8000/mcp/airports" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Unauthorized Call (Should Fail)
```bash
curl -X GET "http://localhost:8000/mcp/airports"
# Returns: 401 Unauthorized
```

## 🏷️ VG System Identification

All authenticated responses include VG system metadata:
```json
{
  "flights": [...],
  "_auth_info": {
    "authenticated": true,
    "client_id": "mcp-client-vg",
    "system": "VG_FLIGHTMCP_2024"
  }
}
```

## 🔄 Token Refresh

Tokens expire after 1 hour. Clients should:
1. Check token expiration before each request
2. Request new token when expired
3. Retry failed requests with new token

## 📊 Logging and Monitoring

### OAuth Server Logs
- Token requests and responses
- Client authentication attempts
- Token validation results

### API Server Logs  
- Authenticated API access
- Token validation success/failure
- Request/response metadata

### Log Files
- `src/flight_booking_mcp/auth/oauth_server.log`
- `src/flight_booking_mcp/authenticated_api.log`
- `src/flight_booking_mcp/mcp_tools.log`

## 🎯 Key Benefits

1. **Dual Interface:** MCP for Claude Desktop + HTTP for apps
2. **Secure APIs:** JWT token authentication
3. **Professional Logging:** Comprehensive audit trail
4. **VG Branding:** Subtle system identification
5. **Scalable:** Standard OAuth 2.0 implementation

## 🚀 Next Steps

1. **Run the demo:** `python demo_oauth_complete.py`
2. **Test with Postman:** Import API collection
3. **Build client app:** Use `oauth_client_demo.py` as reference
4. **Monitor logs:** Check authentication flows
5. **Scale up:** Add more OAuth features as needed
