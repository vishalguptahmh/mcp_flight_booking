# VG Flight Booking MCP Server

**Author:** Vishal Gupta  
**System:** VG_FLIGHTMCP_2024  
**Version:** 2.1.0  

A production-ready Model Context Protocol (MCP) server for flight booking operations with OAuth 2.1 authentication support.

## Features

- **Flight Search**: Search flights between 29 global airports with real-time pricing
- **Flight Booking**: Create and manage flight bookings with VG-prefixed booking IDs
- **User Management**: Track user bookings and history
- **OAuth 2.1 Security**: Complete OAuth authentication with JWT tokens (optional)
- **VG Branding**: Professional system with VG-prefixed flight and booking IDs
- **Comprehensive Logging**: Full audit trail for debugging and monitoring

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd flight_booking_mcp

# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Claude Desktop Configuration

The easiest way to get started is with Claude Desktop. You have two configuration options:

#### Option 1: Simple Setup (No Authentication)

This is the recommended approach for most users. Create or update your Claude Desktop configuration file at `~/.config/claude-desktop/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "flight-booking": {
      "command": "/path/to/your/project/.venv/bin/flight-booking-mcp",
      "args": ["--stdio"],
      "env": {
        "OAUTH_ENABLED": "false"
      }
    }
  }
}
```

#### Option 2: With OAuth Authentication

If you need authentication features, use this configuration:

```json
{
  "mcpServers": {
    "flight-booking": {
      "command": "/path/to/your/project/.venv/bin/flight-booking-mcp", 
      "args": ["--stdio"],
      "env": {
        "OAUTH_ENABLED": "true",
        "OAUTH_SERVER_URL": "http://localhost:9000",
        "CLIENT_ID": "claude-desktop-client",
        "CLIENT_SECRET": "claude-desktop-secret"
      }
    }
  }
}
```

### Running the System

#### For Claude Desktop (Recommended)

1. Configure Claude Desktop using one of the options above
2. If using OAuth, start the OAuth server first:
   ```bash
   cd flight_booking_mcp
   .venv/bin/python -m flight_booking_mcp.auth.oauth_server
   ```
3. Restart Claude Desktop
4. Flight booking tools will be available in Claude Desktop

#### For Development and Testing

```bash
# Run MCP server in HTTP mode
.venv/bin/flight-booking-mcp

# Run OAuth server (separate terminal)
.venv/bin/python -m flight_booking_mcp.auth.oauth_server
```

## Available Tools

### Flight Operations

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_available_airports` | Get list of all 29 supported airports | None |
| `search_flights` | Search flights between airports | `origin`, `destination`, `date` |
| `create_booking` | Create a flight booking | `flight_id`, `passenger_name`, `email` |
| `get_user_bookings` | Get user's booking history | `email` |

### OAuth Authentication (Optional)

| Tool | Description | Parameters |
|------|-------------|------------|
| `authenticate_with_vscode` | VS Code style OAuth authentication | None |

## VS Code Integration

The system includes VS Code-style authentication that mimics how VS Code handles OAuth flows (like GitHub authentication).

### Using VS Code Authentication

1. **Start OAuth Server**:
   ```bash
   cd flight_booking_mcp
   .venv/bin/python -m flight_booking_mcp.auth.oauth_server
   ```

2. **Test VS Code Authentication**:
   ```bash
   python test_vscode_auth.py
   ```

3. **Use in Claude Desktop**:
   Simply ask Claude to authenticate with VS Code:
   ```
   Authenticate with VS Code for flight booking
   ```

### Authentication Flow

The VS Code authentication process:

1. Shows authorization popup (simulated)
2. Opens browser to OAuth login page
3. User logs in with demo credentials (demo-user/demo-pass)
4. Browser redirects back to application
5. Access token stored securely
6. Ready for flight booking operations

### Supported OAuth Clients

- **claude-desktop-client** - For Claude Desktop integration
- **vscode-mcp-client** - For VS Code extensions
- **vg-desktop-client** - For desktop applications
- **mcp-client** - For general MCP usage

## Example Usage

### Search Flights

You can search for flights using natural language:

```
Search for flights from Pune to Delhi on 2024-12-01
```

The system will return available flights with details like:

```json
{
  "flights": [
    {
      "id": "VG123",
      "origin": "PNQ", 
      "destination": "DEL",
      "price": 4937,
      "departure": "08:00",
      "arrival": "11:30",
      "airline": "SkyConnect"
    }
  ]
}
```

### Create Booking

To book a flight, simply ask:

```
Book flight VG123 for John Doe with email john@example.com
```

You'll receive a confirmation with a VG-prefixed booking ID:

```json
{
  "booking_id": "VGAA7324",
  "flight_id": "VG123", 
  "status": "confirmed",
  "confirmation_code": "CONFVGAA7324"
}
```

## Architecture

The project follows a clean, modular architecture:

```
flight_booking_mcp/
├── src/flight_booking_mcp/
│   ├── server.py              # Main MCP server
│   ├── tools.py               # MCP tool definitions  
│   ├── resources.py           # MCP resource definitions
│   ├── auth/                  # OAuth authentication (optional)
│   │   ├── oauth_server.py    # OAuth 2.1 authorization server
│   │   └── token_validator.py # JWT token validation
│   ├── config/                # Configuration management
│   │   ├── mcp_config.py      # MCP server configuration
│   │   └── auth_config.py     # OAuth configuration
│   ├── services/              # Business logic
│   │   └── flight_service.py  # Flight operations
│   ├── models/                # Data models
│   └── data/
│       └── airports.json      # Airport database (29 airports)
├── tests/                     # Unit tests
├── docs/                      # Documentation
└── README.md
```

## Security Features

When OAuth is enabled, the system provides:

- **OAuth 2.1 Compliance**: Following the latest OAuth standards
- **JWT Tokens**: Industry-standard token-based authentication
- **Client Validation**: Only authorized clients can access the system
- **Audit Logging**: Comprehensive request/response logging
- **VG System Tags**: All components are tagged for tracking and identification

## Supported Airports

The system currently supports 29 major airports worldwide, including:

**India**: PNQ (Pune), DEL (Delhi), BOM (Mumbai), BLR (Bangalore), MAA (Chennai), CCU (Kolkata), COK (Kochi), HYD (Hyderabad), AMD (Ahmedabad), GOI (Goa), JAI (Jaipur), LKO (Lucknow), and more

**International**: LHR (London), JFK (New York), DXB (Dubai), CDG (Paris), HND (Tokyo), SYD (Sydney), FRA (Frankfurt)

## Development

### Running Tests

```bash
pytest tests/
```

### Requirements

- **Python 3.13+** required
- **FastMCP** for MCP protocol implementation
- **FastAPI** for OAuth server
- **Pydantic** for data validation
- **PyJWT** for token handling

## Documentation

Additional documentation is available in the `docs/` directory:

- [OAuth Architecture](docs/OAUTH_ARCHITECTURE.md)
- [Logging Guide](docs/LOGGING_GUIDE.md) 
- [OAuth Deployment](docs/README_OAUTH_DEPLOYMENT.md)

## OAuth Server Credentials

When using OAuth authentication, you can test with these demo credentials:

- **Username**: `demo-user`
- **Password**: `demo-pass`
- **OAuth Server**: `http://localhost:9000`

## System Identification

All components in the VG Flight Booking system are tagged with `VG_FLIGHTMCP_2024` for easy identification:

- Flight IDs follow the pattern: `VG123`, `VG456`, etc.
- Booking IDs follow the pattern: `VGAA7324`, `VGBB8901`, etc.
- All API responses include VG system signatures

## License

© 2024 Vishal Gupta. All rights reserved.

---

**VG Flight Booking MCP** - Professional flight booking integration for Claude Desktop
