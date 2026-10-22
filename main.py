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

@app.get("/")
def home():
    return {"status": "OSINT Image Search Engine Online"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    contents = await file.read()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Upload ke Litterbox Catbox (direct link tanpa proteksi bot)
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
                
    return {"success": False, "error": "Gagal mengunggah gambar ke server CDN"}
