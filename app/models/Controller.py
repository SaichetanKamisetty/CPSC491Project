from Model import DetectBubbles, DetectText, RemoveText, TranslateText, ProcessOutput


from roboflow import Roboflow
rf = Roboflow(api_key="")
project = rf.workspace().project("segmetn")
model = project.version(3).model
from manga_ocr import MangaOcr 

ocr = MangaOcr()

class TranslateWebtoons():
    def __init__(self, file_loc): 
        self.file_loc = file_loc

    def TranslateWebtoon(self):
        speechBubbles = DetectBubbles(roboflowModel=model, directory=self.file_loc).DetectBubble()
        detectedText = DetectText(predictions=speechBubbles, mangaOCR=ocr).DetectText()
        # for i in detectedText.keys():
        #     for j in range(len(detectedText[i])):
        #         print(detectedText[i][j]['text'])
        RemoveText(directory=self.file_loc, predictions=speechBubbles).RemoveText()
        # TranslateText()
        # ProcessOutput()


translator = TranslateWebtoons(r"C:\Users\cheta\OneDrive\Desktop\CPSC491Project\app\static\uploads")

translator.TranslateWebtoon()