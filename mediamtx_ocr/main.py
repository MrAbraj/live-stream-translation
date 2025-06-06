import cv2
import numpy as np
import subprocess
import threading
import queue
import time
from PIL import Image, ImageDraw 
from craft_text_detector import Craft
import pytesseract

from ocr import ocrDetectionInpaiting
from translate import get_translated_dict
from utility import fetchDisplayStreamKey, is_frame_different, normalize_quotes, generate_text_mask, estimate_text_thickness, get_dominant_color_craft, compute_optimal_font_scale

displayStreamKey = fetchDisplayStreamKey()
ocrTranslatedStreamKeyHindi = "ocr-translated-stream-hindi"

rtsp_url = f"rtsp://localhost:8554/{displayStreamKey}"
rtmp_url = f"rtmp://localhost/{ocrTranslatedStreamKeyHindi}"

frame_queue = queue.Queue(maxsize=5)
last_redrawn_frame = None
prev_frame_rgb = None
lock = threading.Lock()
frame_counter = 0

cap = cv2.VideoCapture(f"{rtsp_url}?buffer_size=1")
if not cap.isOpened():
    raise Exception("Failed to open RTSP stream.")

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)
fps = cap.get(cv2.CAP_PROP_FPS) or 30

print(f"Connected: {width}x{height} @ {fps}fps")

ffmpeg = subprocess.Popen([
    "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
    "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", str(fps),
    "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
    "-bf", "0", "-x264-params", "keyint=30:min-keyint=30:no-scenecut=1",
    "-f", "flv", rtmp_url
], stdin=subprocess.PIPE)


craft = Craft(output_dir='craft_output', crop_type="box", cuda=False)


def ocr_worker():
    global last_redrawn_frame
    while True:
        try:
            frame_rgb = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        try:
            image_erased = ocrDetectionInpaiting(craft, frame_rgb)
            with lock:
                last_redrawn_frame = image_erased.copy()

        except Exception as e:
            print("Worker exception:", e)
        finally:
            frame_queue.task_done()


threading.Thread(target=ocr_worker, daemon=True).start()


try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if prev_frame_rgb is not None and not is_frame_different(frame_rgb, prev_frame_rgb, threshold=5000):

            print("Frame is similar to previous. Skipping OCR processing.")
            with lock:
                frame_to_send = last_redrawn_frame if last_redrawn_frame is not None else frame
            ffmpeg.stdin.write(frame_to_send.tobytes())
            continue

        prev_frame_rgb = frame_rgb.copy()

        if not frame_queue.full():
            frame_queue.put_nowait(frame_rgb)

        with lock:
            frame_to_send = last_redrawn_frame if last_redrawn_frame is not None else frame

        try:
            ffmpeg.stdin.write(frame_to_send.tobytes())
        except BrokenPipeError:
            print("FFmpeg pipe broken. Exiting main loop.")
            break

except KeyboardInterrupt:
    print("Interrupted by user.")


cap.release()
craft.unload_craftnet_model()
craft.unload_refinenet_model()
try:
    ffmpeg.stdin.close()
    ffmpeg.wait()
except Exception as e:
    print("Error closing FFmpeg:", e)

print("Resources released.")
