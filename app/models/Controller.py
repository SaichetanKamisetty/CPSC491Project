from Model import DetectBubbles, DetectText, RemoveText, TranslateText, ProcessOutput

class TranslateManga():
    def __init__(self, file_loc, model, ocr): 
        self.file_loc = file_loc
        self.model = model
        self.ocr = ocr

    def TranslateManga(self):
        try:
            speechBubbles = DetectBubbles(roboflowModel=self.model, directory=self.file_loc).DetectBubble()
            # detectedText = DetectText(predictions=speechBubbles, mangaOCR=self.ocr).DetectText() # Implement later
            # for i in detectedText.keys():
            #     for j in range(len(detectedText[i])):
            #         print(detectedText[i][j]['text'])
            RemoveText(directory=self.file_loc, predictions=speechBubbles).RemoveText()
            
        except Exception as err:
            print(err)
            return 0
        
        return 1
        # TranslateText()
        # ProcessOutput()


# translator = TranslateManga(r"C:\Users\cheta\OneDrive\Desktop\CPSC491Project\app\static\uploads")

# translator.TranslateWebtoon()