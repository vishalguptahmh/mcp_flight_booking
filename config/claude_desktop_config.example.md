# Example Claude Desktop Configuration

This file shows how to configure Claude Desktop to use the VG Flight Booking MCP server.

## Configuration File Location

- **macOS**: `~/.config/claude-desktop/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

## Simple Configuration (No Authentication)

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

## OAuth Configuration (With Authentication)

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

## Notes

1. Replace `/path/to/your/project/.venv/bin/flight-booking-mcp` with the actual path to your virtual environment
2. When using OAuth, make sure to start the OAuth server first: `.venv/bin/python -m flight_booking_mcp.auth.oauth_server`
3. Restart Claude Desktop after making configuration changes
4. OAuth demo credentials: username=`demo-user`, password=`demo-pass`
