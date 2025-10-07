
from flask import Flask, request, jsonify, send_file
import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import google.oauth2.credentials

app = Flask(__name__)

def get_credentials_from_request():
    data = request.json if request.is_json else request.form
    token = data.get('token')
    refresh_token = data.get('refresh_token')
    token_uri = data.get('token_uri')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    scopes = data.get('scopes')
    if not token or not token_uri or not client_id or not client_secret or not scopes:
        return None
    creds = google.oauth2.credentials.Credentials(
        token=token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )
    return creds

@app.route('/mcp/drive/list', methods=['POST'])
def list_files():
    creds = get_credentials_from_request()
    if not creds:
        return jsonify({"error": "Missing or invalid credentials"}), 400
    drive_service = build('drive', 'v3', credentials=creds)
    results = drive_service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return jsonify({"files": items})

@app.route('/mcp/drive/upload', methods=['POST'])
def upload_file():
    creds = get_credentials_from_request()
    if not creds:
        return jsonify({"error": "Missing or invalid credentials"}), 400
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    drive_service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': file.filename}
    media = MediaFileUpload(file, mimetype=file.content_type)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media).execute()
    return jsonify({"status": "uploaded", "file": uploaded})

@app.route('/mcp/drive/download', methods=['POST'])
def download_file():
    creds = get_credentials_from_request()
    if not creds:
        return jsonify({"error": "Missing or invalid credentials"}), 400
    data = request.json if request.is_json else request.form
    file_id = data.get('file_id')
    if not file_id:
        return jsonify({"error": "No file_id provided"}), 400
    drive_service = build('drive', 'v3', credentials=creds)
    request_download = drive_service.files().get_media(fileId=file_id)
    file_data = io.BytesIO()
    downloader = MediaIoBaseDownload(file_data, request_download)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    file_data.seek(0)
    # For API, return as base64 or as a file download; here, just return success
    return send_file(file_data, as_attachment=True, download_name='downloaded_file')

if __name__ == '__main__':
    app.run(port=6000, debug=True)
