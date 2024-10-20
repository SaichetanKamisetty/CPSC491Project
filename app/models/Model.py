
from PIL import Image, ImageDraw, ImageFont
# import textwrap
import cv2
import numpy as np
import os

class DetectBubbles:
    def __init__(self, roboflowModel, directory):
        self.roboflowModel = roboflowModel
        self.directory = directory

    def DetectBubble(self):
        if not os.path.isdir(self.directory):
            print(f"The specified path {self.directory} is not a directory.")
            return {}
        
        bubble_dict = {}
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                detectedBubbles = self.roboflowModel.predict(file_path, confidence=40).json()
                bubble_dict[file_path] = detectedBubbles

        return bubble_dict
        
class DetectText:
    def __init__(self, predictions, mangaOCR):
        self.predictions = predictions
        self.mangaOCR = mangaOCR

    def DetectText(self):
        text_map = {}

        for page in self.predictions.keys():
            image = Image.open(page)
            areas = []
            for prediction in self.predictions[page]['predictions']:
                x, y = prediction['x'], prediction['y']
                width, height = prediction['width'], prediction['height']
                points = prediction['points']

                x_min = x - width / 2
                y_min = y - height / 2
                x_max = x + width / 2
                y_max = y + height / 2

                roi = image.crop((x_min, y_min, x_max, y_max)).convert("RGB")
                text = self.mangaOCR(roi)
            
                pg = {
                    "text_box": (x_min, y_min, x_max, y_max),
                    "points": points,
                    "text": text
                }
                areas.append(pg)

            text_map[page] = areas

        return text_map


class RemoveText:
    def __init__(self, directory, predictions):
        self.directory = directory
        self.predictions = predictions

    def RemoveText(self):
        for page in self.predictions.keys():
            image_ = cv2.imread(page)

            for prediction in self.predictions[page]['predictions']:
                points = prediction['points']
                polygon = [(point['x'], point['y']) for point in points]
                polygon_np = np.array(polygon, dtype=np.int32)
                mask = np.zeros(image_.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [polygon_np], 255)               

                inpainted_image = cv2.inpaint(image_, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
                image_ = inpainted_image

            print(page)
            image = Image.fromarray(cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
            image.save(page)

class TranslateText:
    def __init__():
        pass
    def TranslateText():
        pass

class ProcessOutput:
    def __init__():
        pass
    def ProcessOutput():
        pass