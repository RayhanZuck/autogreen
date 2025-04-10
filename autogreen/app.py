from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time

app = FastAPI()

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_URL = "https://rayhanzuck-cloud.hf.space"

app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

MAX_FILE_AGE = 3 * 24 * 60 * 60  
MAX_FILE_SIZE = 100 * 1024 * 1024  

# Counter in memory
total_uploaded_counter = 0

def cleanup_old_files():
    now = time.time()
    deleted = 0
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > MAX_FILE_AGE:
                os.remove(file_path)
                deleted += 1
    return deleted

@app.on_event("startup")
def count_existing_files():
    global total_uploaded_counter
    total_uploaded_counter = len(os.listdir(UPLOAD_FOLDER))

@app.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    global total_uploaded_counter

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

    total_uploaded_counter += 1
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
            "total_all_time_files": total_uploaded_counter
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/", response_class=HTMLResponse)
async def main():
    total_current_files = len(os.listdir(UPLOAD_FOLDER))

    return f"""
    <html>
        <head>
            <title>Simple File Uploader</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    background-color: #f4f6f8;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 30px 40px;
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
                    width: 100%;
                    max-width: 500px;
                }}
                h2 {{
                    color: #1e88e5;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                form {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                input[type="file"] {{
                    display: block;
                    margin: 0 auto 10px auto;
                }}
                .info {{
                    text-align: center;
                    margin: 15px 0;
                    color: #555;
                }}
                ul {{
                    list-style: none;
                    padding: 0;
                    max-height: 200px;
                    overflow-y: auto;
                    margin-bottom: 10px;
                }}
                li {{
                    margin-bottom: 6px;
                    text-align: center;
                }}
                a {{
                    color: #1e88e5;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                button {{
                    display: block;
                    margin: 0 auto;
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
            <div class="container">
                <h2>Upload File</h2>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" required>
                    <input type="submit" value="Upload">
                </form>

                <div class="info">
                    <p><strong>Total files available:</strong> {total_current_files}</p>
                    <p><strong>Total files uploaded:</strong> {total_uploaded_counter}</p>
                </div>

                <h4 style="text-align:center;">Uploaded Files:</h4>
                <ul id="file-list"></ul>
                <button onclick="loadMore()">Load More</button>
            </div>

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
    
