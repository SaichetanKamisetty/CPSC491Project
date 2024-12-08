
from PIL import Image, ImageDraw, ImageFont
import textwrap
import cv2
import numpy as np
import os
from openai import OpenAI

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

                x_min = x - width / 2
                y_min = y - height / 2
                x_max = x + width / 2
                y_max = y + height / 2

                roi = image.crop((x_min, y_min, x_max, y_max)).convert("RGB")
                text = self.mangaOCR(roi)
            
                pg = {
                    "text_box": (x_min, y_min, x_max, y_max),
                    "text": text
                }
                areas.append(pg)

            text_map[page] = areas

        return text_map


class RemoveText:
    def __init__(self, predictions):
        self.predictions = predictions

    def RemoveText(self):
        for page in self.predictions.keys():
            image_ = cv2.imread(page)

            boundary_check = self.predictions[page]['predictions']

            if not boundary_check:
                inpainted_image = image_

            for prediction in self.predictions[page]['predictions']:
                points = prediction['points']
                polygon = [(point['x'], point['y']) for point in points]
                polygon_np = np.array(polygon, dtype=np.int32)
                mask = np.zeros(image_.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [polygon_np], 255)               

                inpainted_image = cv2.inpaint(image_, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
                image_ = inpainted_image

            image = Image.fromarray(cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
            image.save(page)

class TranslateText:
    def __init__(self, text_map, gpt_key):
        self.text_map = text_map
        self.gpt_key = gpt_key
    def TranslateText(self):
        client = OpenAI(api_key=self.gpt_key)
        for page in self.text_map.keys():
            for i, box in enumerate(self.text_map[page]):
                text = box['text']
                try:
                    response = client.chat.completions.create(
                        model = "gpt-4o-mini",
                        messages=[
                            {"role": "system","content":"You are a manga translator. Follow a style that is expressive and interesting, and try to make the translations sound good even if you have to localize it to english. If the given Japanese text is a single character/expression, translate it as an expression. If it is punctuation, do not translate and just send the text back. IMPORTANT: Try and condense where possible to have a shorter response, but still have full meaning. Always try your best, ONLY return a translated phrase, if one cannot be found, try your best."},
                            {"role": "user", "content":f"{text}"}]
                    )
                    self.text_map[page][i]['text'] = response.choices[0].message.content
                except Exception as e:
                    print(f"error: {e}")
                    return [{}, e]
        text_map = self.text_map
        return [text_map, None]

class ProcessOutput:
    def __init__(self, text_map, font_size=100):
        self.text_map = text_map
        self.font_size = font_size
    def ProcessOutput(self):
         for page in self.text_map.keys():
            img = Image.open(page)
            draw = ImageDraw.Draw(img)
            for box in self.text_map[page]:
                x_min, y_min, x_max, y_max = box['text_box']

                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2

                max_width = x_max - x_min
                max_height = y_max - y_min

                text = box['text']
                text_height = None

                font_size = self.font_size

                while True:
                    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                    font = ImageFont.truetype(f"{BASE_DIR}/animeace2_bld.ttf", size=font_size)
                    space_bbox = font.getbbox("a")
                    space_width = int(space_bbox[2] - space_bbox[0]) 
                    if space_width == 0:
                        space_width = 1
                    if int(max_width // space_width) <=  0:
                        wid = space_width
                    else:
                        wid = int(max_width // space_width)
                    wrapped_text = textwrap.fill(text=text, width=wid, break_long_words=False)
                    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    if text_height > max_height or text_width > max_width:
                        font_size -= 1
                    else:
                        break

                if text_height < 0.4 * max_height:  # If text is less than 80% of max height
                    max_width *= 1.4
                    while text_height < max_height and text_width <= max_width:
                        font_size += 1
                        font = ImageFont.truetype(f"{BASE_DIR}/animeace2_bld.ttf", size=font_size)
                        wrapped_text = textwrap.fill(text=text, width=wid, break_long_words=False, replace_whitespace=False)
                        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]

                bbox = draw.textbbox((0, 0), wrapped_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                text_x = center_x - text_width // 2
                text_y = center_y - text_height // 2
                draw.multiline_text((text_x, text_y), wrapped_text, font=font, fill="black")
            
            img.save(page)
