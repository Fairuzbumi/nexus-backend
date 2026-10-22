import base64
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

@app.get("/")
def home():
    return {"status": "OSINT Image Search Engine Online"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        b64_image = base64.b64encode(contents).decode('utf-8')
        
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            # 1. API FreeImage.host (Base64 - Anti Block)
            try:
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

            # 2. Fallback: Catbox dengan Browser Header
            try:
                data = {"reqtype": "fileupload"}
                files = {'fileToUpload': (file.filename or "image.jpg", contents, file.content_type or "image/jpeg")}
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

        return {"success": False, "error": "Gagal mengunggah gambar ke CDN temporary."}

    except Exception as e:
        return {"success": False, "error": f"Server error: {str(e)}"}
