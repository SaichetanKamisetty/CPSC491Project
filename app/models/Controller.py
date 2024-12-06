from Model import DetectBubbles, DetectText, RemoveText, TranslateText, ProcessOutput

class TranslateManga():
    def __init__(self, file_loc, model, ocr, progress_callback, api_key, text_size=100): 
        self.file_loc = file_loc
        self.model = model
        self.ocr = ocr
        self.progress_callback = progress_callback
        self.api_key = api_key
        self.text_size = text_size


    def TranslateManga(self):
        try:
            self.progress_callback("bubbles")
            speechBubbles = DetectBubbles(roboflowModel=self.model, directory=self.file_loc).DetectBubble()
            self.progress_callback("text")
            detectedText = DetectText(predictions=speechBubbles, mangaOCR=self.ocr).DetectText()
            self.progress_callback("cleaning")
            RemoveText(predictions=speechBubbles).RemoveText()
            self.progress_callback("translate")
            translatedText = TranslateText(text_map=detectedText, gpt_key="").TranslateText()
            self.progress_callback("processing")
            ProcessOutput(text_map=translatedText[0]).ProcessOutput()
            self.progress_callback("complete")
            
        except Exception as err:
            print(err)
            return [0, err]
        
        return [1, None]


# translator = TranslateManga(r"C:\Users\cheta\OneDrive\Desktop\CPSC491Project\app\static\uploads")

# translator.TranslateWebtoon()