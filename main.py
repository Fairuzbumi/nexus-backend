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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://yandex.com",
    "Referer": "https://yandex.com/images/"
}

@app.get("/")
def home():
    return {"status": "OSINT Image Search Engine Online"}

@app.post("/api/search")
async def search_image(file: UploadFile = File(...)):
    contents = await file.read()
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        files = {'upfile': (file.filename, contents, file.content_type)}
        response = await client.post(
            'https://yandex.com/images-apphost/image-downloading',
            files=files,
            headers=HEADERS,
            params={'rpt': 'imageview'}
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                image_id = data.get("image_id")
                shard = data.get("image_shard", "")
                yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={shard}/{image_id}"
                return {
                    "success": True,
                    "yandex_url": yandex_url,
                    "message": "Pencarian Yandex berhasil"
                }
            except Exception as e:
                return {"success": False, "error": f"Response JSON invalid: {str(e)}"}
        
        return {
            "success": False, 
            "error": f"Yandex menolak koneksi (Status code: {response.status_code})"
        }
