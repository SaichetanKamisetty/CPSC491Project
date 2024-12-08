from Model import DetectBubbles, DetectText, RemoveText, TranslateText, ProcessOutput
import logging
import time

logging.basicConfig(level=logging.INFO, filename='manga_translation.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TranslateManga():
    def __init__(self, file_loc, model, ocr, progress_callback, api_key, remove_text_only, text_size=100): 
        self.file_loc = file_loc
        self.model = model
        self.ocr = ocr
        self.progress_callback = progress_callback
        self.api_key = api_key
        self.text_size = text_size
        self.remove_text_only = remove_text_only

    def log_sli(self, step, success, duration=None):
        message = f"{step} - Success: {success}"
        if duration is not None:
            message += f", Duration: {duration:.2f}s"
        logging.info(message)

    def TranslateManga(self):
        try:

            start_time = time.time()

            self.progress_callback("bubbles")
            bubble_start_time = time.time()
            speechBubbles = DetectBubbles(roboflowModel=self.model, directory=self.file_loc).DetectBubble()
            bubble_duration = time.time() - bubble_start_time
            self.log_sli("Bubble Detection", success=len(speechBubbles.keys()), duration=bubble_duration)

            self.progress_callback("text")
            text_start_time = time.time()
            detectedText = DetectText(predictions=speechBubbles, mangaOCR=self.ocr).DetectText()
            text_duration = time.time() - text_start_time
            self.log_sli("Text Detection", success=len(detectedText), duration=text_duration)

            self.progress_callback("cleaning")
            clean_start_time = time.time()
            RemoveText(predictions=speechBubbles).RemoveText()
            clean_duration = time.time() - clean_start_time
            self.log_sli("Text Removal", success=len(speechBubbles), duration=clean_duration)

            if self.remove_text_only:
                self.progress_callback("complete")
                total_duration = time.time() - start_time
                self.log_sli("Total Process Time", success=True, duration=total_duration)
                return [1, None]
            
            self.progress_callback("translate")
            translate_start_time = time.time()
            translatedText = TranslateText(text_map=detectedText, gpt_key=self.api_key).TranslateText()
            translate_duration = time.time() - translate_start_time
            self.log_sli("Text Translation", success=len(detectedText), duration=translate_duration)


            self.progress_callback("processing")
            output_start_time = time.time()
            ProcessOutput(text_map=translatedText[0], font_size=self.text_size).ProcessOutput()
            output_duration = time.time() - output_start_time
            self.log_sli("Output Processing", success=len(detectedText), duration=output_duration)

            self.progress_callback("complete")
            total_duration = time.time() - start_time
            self.log_sli("Total Process Time", success=True, duration=total_duration)
            
        except Exception as err:
            print(err)
            return [0, err]
        
        return [1, None]