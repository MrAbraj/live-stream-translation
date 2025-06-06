
from ocr import ocrDetectionInpaiting
from craft_text_detector import Craft

craft = Craft(output_dir='craft_output', crop_type="box", cuda=False)

# read image from the file and send to the 
# ocrDetectionInpaiting function
import cv2
import numpy as np
def read_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image at {image_path} could not be read.")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
result_img = ocrDetectionInpaiting(craft, read_image("blood.png"))
# output_path = "final_output.png"
    # cv2.imwrite(output_path, image_erased)
    # print(f"Final image saved to {output_path}")
    # Image.open(output_path).show()