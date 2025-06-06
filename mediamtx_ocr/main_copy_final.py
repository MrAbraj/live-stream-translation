import cv2
import numpy as np
import subprocess
import threading
import queue
import time
from PIL import Image, ImageDraw 
from craft_text_detector import Craft
import pytesseract

from translate import get_translated_dict
from utility import fetchDisplayStreamKey, is_frame_different, normalize_quotes, generate_text_mask, estimate_text_thickness, get_dominant_color_craft, compute_optimal_font_scale

displayStreamKey = fetchDisplayStreamKey()
ocrTranslatedStreamKeyHindi = "ocr-translated-stream-hindi"
font_path = "assets/font/NotoSans-Italic-VariableFont_wdth,wght.ttf"
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

# === CRAFT Setup ===
craft = Craft(output_dir='craft_output', crop_type="box", cuda=False)

# === Worker Thread ===
def ocr_worker():
    global last_redrawn_frame
    while True:
        try:
            frame_rgb = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        try:
            image_erased = frame_rgb.copy()
            prediction_result = craft.detect_text(frame_rgb)
            boxes = prediction_result['boxes']
            text_info_list = []
            result_dict = {}

            for i, box in enumerate(boxes):
                try:
                    
                    pts = np.array(box, dtype=np.int32).reshape((-1, 1, 2))
                except Exception as e:
                    print(f"Skipping box {i} due to reshape error: {e}")
                    continue

                
                x, y, w, h = cv2.boundingRect(pts)
                if w < 5 or h < 5: # Skip very small boxes
                    print(f"Skipping small box {i} (w: {w}, h: {h})")
                    continue

            
                pad = 5
                x1 = max(x - pad, 0)
                y1 = max(y - pad, 0)
                x2 = min(x + w + pad, frame_rgb.shape[1])
                y2 = min(y + h + pad, frame_rgb.shape[0])

            
                if x2 <= x1 or y2 <= y1:
                    print(f"Skipping box {i} due to invalid ROI dimensions after padding.")
                    continue

                roi = frame_rgb[y1:y2, x1:x2].copy() 
                
                text = pytesseract.image_to_string(roi, lang='eng', config='--psm 6').strip()
                cleaned_text = normalize_quotes(text)
                result_dict[str(i)] = cleaned_text
                # text = get_hindi_text(i)
                print(f"{i}: '{text}'")
                
                roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            
                text_mask = generate_text_mask(roi_gray)

                thickness = estimate_text_thickness(text_mask)  
                
                color = get_dominant_color_craft(roi, text_mask)

                roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(roi_pil)

                font, font_size = compute_optimal_font_scale(text, w, h, font_path, thickness)
                
                dummy_img = Image.new("RGB", (w, h))
                dummy_draw = ImageDraw.Draw(dummy_img)
                bbox = dummy_draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]

                # Center text vertically in bounding box
                text_y_position = y + (h - th) // 2
                text_x_position = x 
                

            
                text_info_list.append({
                    "text": cleaned_text,
                    "position": (text_x_position, text_y_position),
                    "font": font,
                    "color": color, 
                    "thickness": thickness,
                    "index": i
                })

            
                if pts.shape[0] >= 3: 
                    cv2.fillPoly(image_erased, [pts], color=(255, 255, 255))
                else:
                    print(f"Warning: Bounding box {i} has too few points ({pts.shape[0]}) for fillPoly. Skipping erase.")

            translated_dict = get_translated_dict(result_dict)
            # print(f"Translated json dict: '{translated_dict}'")

            image_pil = Image.fromarray(cv2.cvtColor(image_erased, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(image_pil)
            
            for info in text_info_list:
                font = info["font"]
                position = info["position"]
                color = tuple(info["color"])
                index = str(info["index"]) 
                text = translated_dict.get(index, info["text"])
                print(f"Drawing text '{text}' at {position} with color {color} and font size {font.size}")
                draw.text(
                    position,
                    text,
                    font=font,
                    fill=color,
                    # stroke_width=info["thickness"],  # optional: simulate thickness
                    stroke_fill=(0, 0, 0)            # optional: black stroke
                )

            image_erased = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            with lock:
                last_redrawn_frame = image_erased.copy()

        except Exception as e:
            print("Worker exception:", e)
        finally:
            frame_queue.task_done()

# === Start worker thread ===
threading.Thread(target=ocr_worker, daemon=True).start()

# === Main loop (read, write, and enqueue) ===
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if prev_frame_rgb is not None and not is_frame_different(frame_rgb, prev_frame_rgb, threshold=5000):
            # Skip OCR processing
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

# === Cleanup ===
cap.release()
craft.unload_craftnet_model()
craft.unload_refinenet_model()
try:
    ffmpeg.stdin.close()
    ffmpeg.wait()
except Exception as e:
    print("Error closing FFmpeg:", e)

print("Resources released.")
