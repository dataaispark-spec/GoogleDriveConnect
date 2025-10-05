# Google Drive Web App

A Flask-based web application that integrates with Google Drive API to allow users to list, upload, and download files from their Google Drive.

## Features

- Google OAuth 2.0 authentication
- List files from Google Drive
- Upload files to Google Drive
- Download files from Google Drive

## Setup Instructions

1. **Create a Google Cloud Project:**
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Drive API

2. **Create OAuth Credentials:**
   - Go to "Credentials" in the Google Cloud Console
   - Create credentials for OAuth client ID (Web application)
   - Set authorized redirect URIs to `http://localhost:5000/oauth2callback` (for development)
   - Download the JSON file and rename it to `credentials.json` in the project root

3. **Install Dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Access the App:**
   - Open your browser and go to `http://localhost:5000`
   - Click "Login with Google" to authenticate

## Security Notes

- Replace the `app.secret_key` with a secure random key in production
- Use HTTPS in production
- Handle credentials securely (do not commit `credentials.json` to version control)
