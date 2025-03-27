from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time

app = FastAPI()

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Base URL (Ganti dengan URL Space kamu jika sudah deploy)
BASE_URL = "https://rayhanzuck-cloud.hf.space"

# Menyediakan folder statis agar file bisa diakses dari URL
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

@app.get("/", response_class=HTMLResponse)
async def main():
    return f"""
    <html>
        <body>
            <h2>Upload File</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Upload">
            </form>
            <h3>Uploaded Files:</h3>
            <ul id="file-list"></ul>
            <button onclick="loadMore()">Load More</button>
            <script>
                let page = 1;
                let limit = 10;

                async function fetchFiles() {{
                    let response = await fetch(`/files?limit=${{limit}}&page=${{page}}`);
                    let files = await response.json();
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

MAX_FILE_AGE = 3 * 24 * 60 * 60  
MAX_FILE_SIZE = 100 * 1024 * 1024  

def cleanup_old_files():
    """Menghapus file yang lebih dari 3 hari."""
    now = time.time()
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > MAX_FILE_AGE:
                os.remove(file_path)
                print(f"✅ File {filename} dihapus karena sudah lebih dari 3 hari.")
                
@app.post("/upload")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    file_size = 0
    contents = bytearray()
    
    # Baca file dalam potongan kecil untuk menghindari memory overload
    chunk_size = 1024 * 1024  # 1MB per chunk
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File terlalu besar! Maksimum 100MB.")
        contents.extend(chunk)
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
        
    background_tasks.add_task(cleanup_old_files)
    return {"filename": file.filename, "url": f"{BASE_URL}/uploads/{file.filename}", "status": "uploaded"}

@app.get("/files")
async def list_files(limit: int = Query(10, alias="limit"), page: int = Query(1, alias="page")):
    try:
        files = os.listdir(UPLOAD_FOLDER)

        # Urutkan berdasarkan waktu terakhir diubah (baru di atas)
        files_sorted = sorted(files, key=lambda f: os.path.getmtime(os.path.join(UPLOAD_FOLDER, f)), reverse=True)

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_files = files_sorted[start:end]

        file_list = [{"filename": f, "url": f"{BASE_URL}/uploads/{f}"} for f in paginated_files]
        return JSONResponse(content=file_list)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
          
