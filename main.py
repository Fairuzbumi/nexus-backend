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
        # Upload sementara ke CDN publik tanpa butuh API key
        files = {'file': (file.filename, contents, file.content_type)}
        response = await client.post('https://tmpfiles.org/api/v1/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            raw_url = data.get("data", {}).get("url")
            if raw_url:
                # Format ke direct link CDN
                direct_image_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                
                # Buat pencarian Yandex berbasis URL
                yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_image_url}"
                
                return {
                    "success": True,
                    "yandex_url": yandex_url,
                    "image_url": direct_image_url,
                    "message": "Pencarian OSINT berhasil"
                }
                
    return {"success": False, "error": "Gagal mengunggah gambar ke server temporary CDN"}
