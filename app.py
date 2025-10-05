from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a proper secret key in production

# OAuth 2.0 configuration
CLIENT_SECRETS_FILE = "credentials.json"  # Download from Google Cloud Console
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/drive.file']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    try:
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)

        flow.redirect_uri = url_for('oauth2callback', _external=True)

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')

        # Store the state so the callback can verify the auth server response
        session['state'] = state

        return redirect(authorization_url)
    except FileNotFoundError:
        return "Error: credentials.json not found. Please download it from Google Cloud Console and place it in the project root."

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('files'))

@app.route('/files')
def files():
    if 'credentials' not in session:
        return redirect(url_for('login'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    drive_service = build('drive', 'v3', credentials=credentials)

    # List files and folders
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])

    return render_template('files.html', files=items, drive_service=drive_service)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'credentials' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            credentials = google.oauth2.credentials.Credentials(**session['credentials'])
            drive_service = build('drive', 'v3', credentials=credentials)

            file_metadata = {'name': file.filename}
            media = MediaFileUpload(file.stream, mimetype=file.content_type)
            drive_service.files().create(body=file_metadata, media_body=media).execute()

            return redirect(url_for('files'))

    return render_template('upload.html')

@app.route('/download/<file_id>')
def download(file_id):
    if 'credentials' not in session:
        return redirect(url_for('login'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    drive_service = build('drive', 'v3', credentials=credentials)

    request_download = drive_service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(file_data, request_download)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    file_data.seek(0)
    return send_file(file_data, as_attachment=True, download_name='downloaded_file')

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

if __name__ == '__main__':
    app.run(debug=True)
