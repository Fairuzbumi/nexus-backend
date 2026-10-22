import io
import base64
from PIL import Image
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def compress_image(contents: bytes, max_mb: float = 1.2) -> bytes:
    """Kompres gambar jika ukurannya melebihi batas aman Vercel"""
    if len(contents) <= max_mb * 1024 * 1024:
        return contents
    try:
        img = Image.open(io.BytesIO(contents))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize jika resolusi terlalu raksasa
        img.thumbnail((1920, 1920))
        
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=80, optimize=True)
        return output.getvalue()
    except Exception:
        return contents

@app.get("/")
def home():
    return {"status": "OSINT Image Search Engine Online"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    try:
        raw_contents = await file.read()
        # Otomatis kompres jika gambar > 1.2 MB
        contents = compress_image(raw_contents, max_mb=1.2)
        
        async with httpx.AsyncClient(timeout=8.0, headers=HEADERS) as client:
            # 1. Catbox Direct Upload
            try:
                data = {"reqtype": "fileupload"}
                files = {'fileToUpload': ('image.jpg', contents, 'image/jpeg')}
                res = await client.post('https://catbox.moe/user/api.php', data=data, files=files)
                if res.status_code == 200 and res.text.strip().startswith("http"):
                    direct_url = res.text.strip()
                    yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_url}"
                    return {
                        "success": True,
                        "yandex_url": yandex_url,
                        "image_url": direct_url,
                        "message": "Pencarian OSINT berhasil"
                    }
            except Exception:
                pass

            # 2. Fallback FreeImage Base64
            try:
                b64_image = base64.b64encode(contents).decode('utf-8')
                payload = {
                    "key": "6d207e02198a847aa98d0a2a901485a5",
                    "action": "upload",
                    "source": b64_image,
                    "format": "json"
                }
                res = await client.post('https://freeimage.host/api/1/upload', data=payload)
                if res.status_code == 200:
                    res_data = res.json()
                    direct_url = res_data.get("image", {}).get("url")
                    if direct_url:
                        yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_url}"
                        return {
                            "success": True,
                            "yandex_url": yandex_url,
                            "image_url": direct_url,
                            "message": "Pencarian OSINT berhasil"
                        }
            except Exception:
                pass

        return {"success": False, "error": "Gagal upload ke server CDN"}

    except Exception as e:
        return {"success": False, "error": f"Server error: {str(e)}"}
