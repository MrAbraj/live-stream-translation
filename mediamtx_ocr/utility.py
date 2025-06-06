import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw 
import re
from sklearn.cluster import KMeans
import requests

DOMAIN = "http://192.168.31.221"
API_URL = f"{DOMAIN}:9997/v3/paths/list"

def normalize_quotes(text):
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove leading/trailing unwanted characters
    text = text.lstrip('[{')
    text = text.rstrip(']}."\' ')
    text = text.strip()
    return text

def clean_text_for_match(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

def refine_mask(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    refined = cv2.erode(mask, kernel, iterations=1)
    refined = cv2.dilate(refined, kernel, iterations=1)
    return refined

def get_dominant_color_craft(roi, mask):
    refined_mask = refine_mask(mask)
    text_pixels = roi[refined_mask == 255]

    
    filtered_pixels = text_pixels[(text_pixels > 10).all(axis=1) & (text_pixels < 245).all(axis=1)]
    if len(filtered_pixels) == 0:
        filtered_pixels = text_pixels

  
    sample_lab = cv2.cvtColor(filtered_pixels.reshape(-1,1,3), cv2.COLOR_BGR2LAB).reshape(-1,3)

    kmeans = KMeans(n_clusters=1, n_init=10)
    kmeans.fit(sample_lab)
    dominant_lab = kmeans.cluster_centers_[0].astype(np.uint8).reshape(1,1,3)

   
    dominant_bgr = cv2.cvtColor(dominant_lab, cv2.COLOR_LAB2BGR).reshape(3)

   
    dominant_color = tuple(int(c) for c in dominant_bgr)

    return dominant_color


def estimate_thickness(text_mask):
    mask = (text_mask > 0).astype(np.uint8)
    dist_transform = cv2.distanceTransform(mask, distanceType=cv2.DIST_L2, maskSize=3)
    nonzero_distances = dist_transform[dist_transform > 0]

    if len(nonzero_distances) == 0:
        return 1

    # Use 25th percentile instead of median for thinner thickness
    thickness_estimate = np.percentile(nonzero_distances, 25) * 1.5

    thickness = int(round(thickness_estimate))
    
    # Clamp thickness between 1 and 4 (you can adjust max thickness)
    thickness = max(1, min(thickness, 4))

    return thickness

def estimate_text_thickness(text_mask):
    if cv2.countNonZero(text_mask) == 0:
        return 1
    try:
        return estimate_thickness(text_mask)
    except Exception:
        return 2
    
def generate_text_mask(roi_gray):
    
    _, bin_mask = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    
    foreground_mean = np.mean(roi_gray[bin_mask == 255]) if np.any(bin_mask == 255) else 255
    background_mean = np.mean(roi_gray[bin_mask == 0]) if np.any(bin_mask == 0) else 0

    if foreground_mean > background_mean:
        bin_mask = 255 - bin_mask

    return bin_mask

def compute_optimal_font_scale(
    text, box_width, box_height, font_path,
    min_font_size=5, max_font_size=50,
    shrink_factor=1  # Optional global shrink
):
    for font_size in range(max_font_size, min_font_size - 1, -1):
        font = ImageFont.truetype(font_path, font_size)
        
        dummy_img = Image.new("RGB", (box_width, box_height))
        draw = ImageDraw.Draw(dummy_img)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        if text_width <= box_width and text_height <= box_height:
            # Apply shrink factor for long words or specific languages
            if len(text) > 15 or any(c in text for c in ['ä', 'ö', 'ü', 'ß']):
                adjusted_font_size = int(font_size * shrink_factor)
                adjusted_font = ImageFont.truetype(font_path, adjusted_font_size)
                return adjusted_font, adjusted_font_size
            return font, font_size

    return ImageFont.truetype(font_path, min_font_size), min_font_size

def compute_optimal_font_size_pil(text, box_width, box_height, font_path, max_font_size=100):
    font_size = max_font_size
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = font.getbbox(text)[2:]
        if text_width <= box_width and text_height <= box_height:
            return font_size
        font_size -= 1
    return 10  # fallback


def is_frame_different(frame1, frame2, threshold=1000):
    # Simple absolute difference
    diff = cv2.absdiff(frame1, frame2)
    non_zero_count = np.count_nonzero(diff)

    return non_zero_count > threshold

def fetchDisplayStreamKey ():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        # iterate thr
        for item in items:
            if "display" in item.get("name", ""):
                return item.get("name", "")
        print("No display item found.")
        return ""
    except requests.RequestException as e:
        print(f"Error fetching items: {e}")
        return ""