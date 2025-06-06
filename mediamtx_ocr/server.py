from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from craft_text_detector import Craft
from io import BytesIO
from ocr import ocrDetectionInpaiting

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

craft = Craft(output_dir='craft_output', crop_type="box", cuda=False)

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "Invalid image"}

    result_img = ocrDetectionInpaiting(craft, img)

    # Encode as PNG
    success, img_encoded = cv2.imencode('.png', result_img)
    if not success:
        return {"error": "Failed to encode image"}

    return StreamingResponse(BytesIO(img_encoded.tobytes()), media_type="image/png")

# uvicorn server:app --host 0.0.0.0 --port 8000