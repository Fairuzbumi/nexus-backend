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
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Upload ke Telegraph (super cepat & anti-block)
            files = {'file': (file.filename, contents, file.content_type)}
            response = await client.post('https://telegra.ph/upload', files=files)
            
            if response.status_code == 200:
                res_json = response.json()
                if isinstance(res_json, list) and len(res_json) > 0 and "src" in res_json[0]:
                    path = res_json[0]["src"]
                    direct_image_url = f"https://telegra.ph{path}"
                    yandex_url = f"https://yandex.com/images/search?rpt=imageview&url={direct_image_url}"
                    
                    return {
                        "success": True,
                        "yandex_url": yandex_url,
                        "image_url": direct_image_url,
                        "message": "Pencarian OSINT berhasil"
                    }
        
        return {"success": False, "error": "Gagal upload gambar ke server temporary"}

    except Exception as e:
        return {"success": False, "error": f"Internal server error: {str(e)}"}
