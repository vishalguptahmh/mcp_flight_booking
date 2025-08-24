# Flight Booking MCP Server Package

A properly packaged Model Context Protocol (MCP) server for flight booking with OAuth 2.1 authentication.

## Package Structure

```
flight_booking_mcp/
├── pyproject.toml              # Modern Python package configuration
├── src/
│   └── flight_booking_mcp/     # Main package
│       ├── __init__.py         # Package exports
│       ├── server.py           # Main MCP server
│       ├── auth/               # Authentication module
│       │   ├── __init__.py
│       │   ├── oauth_server.py # OAuth 2.1 server
│       │   └── token_validator.py
│       ├── config/             # Configuration
│       │   ├── __init__.py
│       │   ├── auth_config.py
│       │   └── mcp_config.py
│       ├── models/             # Pydantic models
│       │   └── __init__.py
│       ├── services/           # Business logic
│       │   ├── __init__.py
│       │   └── flight_service.py
│       ├── data/               # Static data
│       │   └── airports.json
│       ├── resources.py        # MCP resources
│       └── tools.py            # MCP tools
└── claude_desktop_config.json  # Claude Desktop configuration
```

## Installation

```bash
# Install in development mode
uv pip install -e .

# Or install from source
uv pip install git+https://github.com/your-repo/flight-booking-mcp.git
```

## Usage

### Console Scripts

The package provides two console scripts:

```bash
# Start MCP server in HTTP mode (default)
flight-booking-mcp

# Start MCP server in stdio mode (for MCP clients)
flight-booking-mcp --stdio

# Start OAuth authorization server
flight-booking-oauth
```

### As a Python Module

```python
from flight_booking_mcp import MCPServer

# Create and run MCP server
server = MCPServer()
mcp = server.create_stdio_server()
mcp.run()
```

### Claude Desktop Integration

Copy the provided `claude_desktop_config.json` to your Claude Desktop configuration:

```bash
# macOS
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Update the paths in the config to match your installation
```

## Features

- ✅ **Proper Python Package**: Modern package structure with `src/` layout
- ✅ **Console Scripts**: Easy command-line access via `flight-booking-mcp`
- ✅ **OAuth 2.1 Authentication**: RFC-compliant OAuth server
- ✅ **MCP Protocol**: Full support for resources, tools, and prompts
- ✅ **Modular Architecture**: Clean separation of concerns
- ✅ **Type Safety**: Full Pydantic model validation
- ✅ **Claude Desktop Ready**: Pre-configured for Claude Desktop

## API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `GET /.well-known/oauth-authorization-server` - OAuth metadata

### Protected Endpoints (OAuth Required)
- `GET /api/airports` - List airports
- `POST /api/search-flights` - Search flights
- `POST /api/bookings` - Create booking
- `GET /api/bookings` - List bookings

## MCP Resources
- `airports` - Airport information database
- `flight-search-help` - Flight search assistance

## MCP Tools
- `search_flights` - Search for flights
- `create_booking` - Create flight booking
- `get_booking_status` - Check booking status

## Development

```bash
# Clone and setup
git clone <repo-url>
cd flight-booking-mcp-package/flight_booking_mcp
uv venv
uv pip install -e .

# Run tests
python -m pytest

# Start development server
.venv/bin/flight-booking-mcp
```

## Configuration

The package uses configuration files in `src/flight_booking_mcp/config/`:
- `auth_config.py` - OAuth server settings
- `mcp_config.py` - MCP server settings

## License

MIT License
