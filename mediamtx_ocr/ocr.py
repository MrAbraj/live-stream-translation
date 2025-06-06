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

font_path = "assets/font/NotoSansDevanagari-VariableFont_wdth,wght.ttf"

def ocrDetectionInpaiting(craft, frame_rgb):
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
    # output_path = "final_output.png"
    # cv2.imwrite(output_path, image_erased)
    # print(f"Final image saved to {output_path}")
    # Image.open(output_path).show()
    return image_erased   