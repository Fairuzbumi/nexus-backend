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
    try:
        contents = await file.read()
        filename = file.filename or "upload.jpg"
        content_type = file.content_type or "image/jpeg"

        # Opsi 1: Try 0x0.st (Super cepat & raw link langsung)
        async with httpx.AsyncClient(timeout=10.0) as client:
            files = {'file': (filename, contents, content_type)}
            res = await client.post('https://0x0.st', files=files)
            if res.status_code == 200 and res.text.strip().startswith("http"):
                direct_url = res.text.strip()
                yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_url}"
                return {
                    "success": True,
                    "yandex_url": yandex_url,
                    "image_url": direct_url,
                    "message": "Pencarian OSINT berhasil"
                }

        # Opsi 2: Fallback ke Catbox
        async with httpx.AsyncClient(timeout=10.0) as client:
            data = {"reqtype": "fileupload"}
            files = {'fileToUpload': (filename, contents, content_type)}
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

        return {"success": False, "error": "Semua server temporary CDN gagal merespons"}

    except Exception as e:
        return {"success": False, "error": f"Server error: {str(e)}"}
