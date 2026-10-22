from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import httpx
import base64

app = FastAPI()

# Biar bisa dipanggil dari web Lovable/Vercel mana aja
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
    # Baca file gambar
    contents = await file.read()
    
    # Bypass SafeSearch / Yandex Direct Reverse Image Endpoint
    # Mengirim foto ke Yandex Visual Search tanpa filter
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {'upfile': (file.filename, contents, file.content_type)}
        response = await client.post(
            'https://yandex.com/images-apphost/image-downloading',
            files=files,
            params={'rpt': 'imageview'}
        )
        
        # Kirim balik URL pencarian Yandex mentah & data hasil
        if response.status_code == 200:
            data = response.json()
            image_id = data.get("image_id")
            yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={data.get('image_shard')}/{image_id}"
            
            return {
                "success": True,
                "yandex_url": yandex_url,
                "message": "Pencarian gambar tanpa SafeSearch berhasil dibuat"
            }
        
    return {"success": False, "error": "Gagal menghubungi Yandex Engine"}