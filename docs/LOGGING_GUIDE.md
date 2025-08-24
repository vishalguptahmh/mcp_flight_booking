# VG Flight MCP Logging Guide
**Author:** Vishal Gupta  
**System:** VG_FLIGHTMCP_2024  

## 📋 Overview
Your MCP server has comprehensive logging that tracks:
- 🔧 MCP tool executions with authentication checks
- 🔐 OAuth authentication attempts and token validation
- 🛠️ Flight service operations (search, booking, etc.)
- 🚨 Security events and authorization failures

## 📍 Log File Locations
Log files are created dynamically when the system runs:
- **MCP Tools:** `src/flight_booking_mcp/mcp_tools.log`
- **OAuth Server:** `src/flight_booking_mcp/auth/oauth_server.log`
- **Token Validation:** `src/flight_booking_mcp/auth/token_validation.log`

## 🚀 How to Monitor Logs

### Real-time Monitoring
```bash
# Watch all logs in real-time
tail -f src/flight_booking_mcp/mcp_tools.log src/flight_booking_mcp/auth/*.log

# Watch specific component
tail -f src/flight_booking_mcp/auth/oauth_server.log
```

## 🔍 What You'll See

### MCP Tool Authentication:
```
🔐 Checking authentication for MCP tool: search_flights
❌ No authentication token found for search_flights
✅ Authentication successful for create_booking
```

### OAuth Token Generation:
```
✅ Token signature validation: SUCCESS
📋 Full Payload: {"sub": "demo-user", "client_id": "vg-desktop-client"}
```

### Security Events:
```
❌ Token validation failed: EXPIRED
🚨 Authorization required for protected endpoint
```

### When Tools are Called:
```
🛠️ Tool execution: search_flights
🔐 OAuth token validation started
🔑 Token validation: SUCCESS
✅ Flight search completed with VG system integration
```

### When OAuth Authentication Happens:
```
🌐 OAuth Request: /oauth/authorize
👤 Client ID: mcp-client
🔐 Authorization code generated: abc12345...
🎫 Token exchange: SUCCESS
```

## 🏷️ System Identification in Logs
All logs include `VG_FLIGHTMCP_2024` system identifiers for tracking and debugging.

## 💡 Next Steps
1. Start `./monitor_logs.sh` in a terminal
2. Configure Claude Desktop with your MCP server
3. Try searching flights or making bookings
4. Watch the comprehensive logs show every step of the process!
