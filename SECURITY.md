# SECURITY NOTICE

🔒 **This project is now secure for GitHub publication**

## Environment Variables Required

Before running this project, you must set up environment variables:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your actual values:
   ```
   JWT_SECRET=your-actual-secret-here
   CLAUDE_DESKTOP_CLIENT_SECRET=your-actual-secret
   # ... etc
   ```

## What Was Fixed

- ✅ Removed all hardcoded secrets from source code
- ✅ Added environment variable validation
- ✅ Created `.env.example` template
- ✅ Updated example files to use placeholder values
- ✅ Added this security notice

## Development vs Production

- **Development**: Use the values in `.env.example` (but change them!)
- **Production**: Generate strong, unique secrets for each environment variable
- **Examples**: All example files now use obvious placeholder values

**⚠️ Never commit your actual `.env` file to Git!**
