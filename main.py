from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

@app.get("/")
def home():
    return {"status": "OSINT Image Search Engine Online"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        async with httpx.AsyncClient(timeout=8.0, headers=HEADERS) as client:
            data = {
                "reqtype": "fileupload",
                "time": "1h"
            }
            files = {'fileToUpload': (file.filename, contents, file.content_type)}
            
            response = await client.post('https://litterbox.catbox.moe/resources/internals/api.php', data=data, files=files)
            
            if response.status_code == 200:
                direct_image_url = response.text.strip()
                if direct_image_url.startswith("http"):
                    yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_image_url}"
                    return {
                        "success": True,
                        "yandex_url": yandex_url,
                        "image_url": direct_image_url,
                        "message": "Pencarian OSINT berhasil"
                    }
    except Exception as e:
        return {"success": False, "error": f"Koneksi gagal: {str(e)}"}

    return {"success": False, "error": "Gagal mengunggah gambar ke Catbox"}
