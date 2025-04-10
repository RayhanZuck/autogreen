from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time

app = FastAPI()

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_URL = "https://rayhanzuck-cloud.hf.space"
COUNT_FILE = "upload_count.txt"

app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

MAX_FILE_AGE = 3 * 24 * 60 * 60  
MAX_FILE_SIZE = 100 * 1024 * 1024  

def increment_upload_count():
    count = get_total_upload_count()
    with open(COUNT_FILE, "w") as f:
        f.write(str(count + 1))

def get_total_upload_count():
    if not os.path.exists(COUNT_FILE):
        return 0
    with open(COUNT_FILE, "r") as f:
        try:
            return int(f.read())
        except ValueError:
            return 0

def cleanup_old_files():
    now = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > MAX_FILE_AGE:
                os.remove(file_path)

@app.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    file_size = 0
    contents = bytearray()
    
    chunk_size = 1024 * 1024
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File terlalu besar! Maksimum 100MB.")
        contents.extend(chunk)
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    increment_upload_count()
    background_tasks.add_task(cleanup_old_files)
    return {"filename": file.filename, "url": f"{BASE_URL}/uploads/{file.filename}", "status": "uploaded"}

@app.get("/files")
async def list_files(limit: int = Query(10), page: int = Query(1)):
    try:
        files = os.listdir(UPLOAD_FOLDER)
        files_sorted = sorted(files, key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)

        start = (page - 1) * limit
        end = start + limit
        paginated_files = files_sorted[start:end]

        file_list = [{"filename": f, "url": f"{BASE_URL}/uploads/{f}"} for f in paginated_files]

        return {
            "files": file_list,
            "total_files": len(files_sorted),
            "total_all_time_files": get_total_upload_count()
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def main():
    total_current_files = len(os.listdir(UPLOAD_FOLDER))
    total_all_time_files = get_total_upload_count()

    return f"""
    <html>
        <head>
            <title>Simple File Uploader</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    max-width: 700px;
                    margin: 40px auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                    color: #333;
                    border-radius: 10px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                }}
                h2 {{
                    color: #1e88e5;
                }}
                form {{
                    margin-bottom: 20px;
                }}
                input[type="file"] {{
                    margin-bottom: 10px;
                }}
                .info {{
                    margin: 10px 0;
                    font-size: 15px;
                    color: #555;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                a {{
                    color: #1e88e5;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                button {{
                    background-color: #1e88e5;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #1565c0;
                }}
            </style>
        </head>
        <body>
            <h2>Upload File</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <br>
                <input type="submit" value="Upload">
            </form>

            <div class="info">
                <p><strong>Total files available:</strong> {total_current_files}</p>
                <p><strong>Total files uploaded:</strong> {total_all_time_files}</p>
            </div>

            <h3>Uploaded Files:</h3>
            <ul id="file-list"></ul>
            <button onclick="loadMore()">Load More</button>

            <script>
                let page = 1;
                let limit = 10;

                async function fetchFiles() {{
                    let response = await fetch(`/files?limit=${{limit}}&page=${{page}}`);
                    let data = await response.json();
                    let files = data.files;
                    let fileList = document.getElementById("file-list");
                    files.forEach(f => {{
                        let li = document.createElement("li");
                        li.innerHTML = `<a href="${{f.url}}" target="_blank">${{f.filename}}</a>`;
                        fileList.appendChild(li);
                    }});
                }}

                function loadMore() {{
                    page++;
                    fetchFiles();
                }}

                fetchFiles();
            </script>
        </body>
    </html>
    """
    