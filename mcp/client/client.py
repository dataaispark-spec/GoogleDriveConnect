import requests

MCP_SERVER_URL = "http://localhost:6000/mcp/drive"

def list_files(token):
    resp = requests.post(f"{MCP_SERVER_URL}/list", json={"token": token})
    return resp.json()

def upload_file(token, file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(f"{MCP_SERVER_URL}/upload", files=files, data={"token": token})
    return resp.json()

def download_file(token, file_id):
    resp = requests.post(f"{MCP_SERVER_URL}/download", json={"token": token, "file_id": file_id})
    return resp.json()
