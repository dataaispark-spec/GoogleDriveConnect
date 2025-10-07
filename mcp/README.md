# MCP Server/Client for Google Drive

This directory contains a minimal Model Context Protocol (MCP) server and client for Google Drive integration.

## Server
- Located in `server/server.py`
- Exposes endpoints for listing, uploading, and downloading files from Google Drive (to be implemented)
- Run with: `python server/server.py`

## Client
- Located in `client/client.py`
- Provides Python functions to interact with the MCP server

## Integration
- The server is a placeholder and should be connected to Google Drive API using OAuth tokens
- The client expects a valid token and file paths/IDs

## Next Steps
- Implement Google Drive logic in the server endpoints
- Use the client to interact with the server from your app or scripts
