import re
import os
import difflib

import cv2
# import onnxruntime
import numpy as np
import torch
import pywinctl as pwc
import pyautogui
import pytesseract
import imutils
import keyboard

from PyQt6.QtCore import pyqtSignal, QSettings, QThread
from PyQt6.QtGui import QKeySequence


class DeepwokenOCR(QThread):
    addCardsSignal = pyqtSignal(list)
    loadingSignal = pyqtSignal(bool)
    
    def __init__(self, helper):
        super(DeepwokenOCR, self).__init__(helper)
        
        from src.gui import DeepwokenHelper
        self.helper: DeepwokenHelper = helper
        
        pytesseract.pytesseract.tesseract_cmd = r'./tesseract/tesseract'
        
        settings = QSettings("Tuxsuper", "DeepwokenHelper")
        
        self.giveFocus = settings.value("giveFocus", False, bool)
        
        hotkey = settings.value("screenshotHotkey1", QKeySequence("J"), QKeySequence)
        self.hotkey1 = hotkey.toString(QKeySequence.SequenceFormat.NativeText)
        
        hotkey = settings.value("screenshotHotkey2", type=QKeySequence)
        self.hotkey2 = hotkey.toString(QKeySequence.SequenceFormat.NativeText)
        
    def run(self):
        model_file_path = './assets/ocr_model.onnx'
        # # ort_session = onnxruntime.InferenceSession(model_file_path)
        # self.model = torch.hub.load('ultralytics/yolov5', 'custom', model_file_path)
        self.model = torch.hub.load('./yolov5', 'custom', model_file_path, source='local')
        
        self.main()


    def get_window_log(self):
        log_location = os.environ['LOCALAPPDATA'] + r"\Roblox\logs"
        search_pattern = r"\[FLog::SurfaceController\] \[_:1\]::replaceDataModel: \(stage:0, window = (\S+?)\)"
        
        active_window_id = pwc.getActiveWindow().getHandle()
        
        files_in_folder = os.listdir(log_location)
        text_files = [file for file in files_in_folder if file.endswith(".log")]
        text_files_sorted = sorted(text_files, key=lambda x: os.path.getmtime(os.path.join(log_location, x)), reverse=True)

        for text_file in text_files_sorted:
            file_path = os.path.join(log_location, text_file)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                match = re.search(search_pattern, content)

                if match:
                    hex_value = match.group(1)
                    decimal_value = int(hex_value, 16)

                    if active_window_id == decimal_value:
                        return file_path


    def get_choice_type(self, log_path):
        if not log_path:
            return
        
        with open(log_path, 'r') as file:
            lines = file.readlines()

        reversed_lines = reversed(lines)

        for line in reversed_lines:
            line = line.strip()
            search_pattern = r"\[FLog::Output\] choicetype: (\w+)"
            match = re.search(search_pattern, line)

            if match:
                choice_type = match.group(1)
                return choice_type


    def get_type_card(self):
        if self.choice_type == "Talent":
            return self.helper.data.all_talents
        
        elif self.choice_type == "Whisper":
            return self.helper.data.all_mantras
        
        elif self.choice_type == "Trait":
            return self.helper.data.traits
        
        return self.helper.data.all_strings


    def get_closest_match(self, target_string):
        max_similarity = 0.0
        closest_match = None

        for card_key, card in self.get_type_card().items():
            card_name = card.get("name") or card_key
            card_name = re.sub(r' \[[A-Za-z]{3}\]', '', card_name)

            similarity = difflib.SequenceMatcher(None, target_string, card_name).ratio()

            if similarity >= 0.5:
                if similarity > max_similarity:
                    max_similarity = similarity
                    closest_match = card

        return closest_match
    
    def extract_text(self, img):
        best_max_val = 0
        best_max_loc = None
        best_tmplt_size = None
        
        tmplt = cv2.imread('./assets/banner-mask.png', cv2.IMREAD_GRAYSCALE)
        paint_tmptl = cv2.imread('./assets/paint-mask.png', cv2.IMREAD_GRAYSCALE)

        for idx in range(50):
            scaled_tmplt = imutils.resize(tmplt.copy(), width=img.shape[1]-idx, inter=cv2.INTER_NEAREST_EXACT)
            
            corrimg = cv2.matchTemplate(img, scaled_tmplt, cv2.TM_CCORR_NORMED, mask=scaled_tmplt)
            _, max_val, _, max_loc = cv2.minMaxLoc(corrimg)
            
            if max_val > best_max_val:
                best_max_val = max_val
                best_max_loc = max_loc
                best_tmplt_size = scaled_tmplt.shape[::-1]
                
                
        
        ww, hh = best_tmplt_size
        xx, yy = best_max_loc
        
        tmplt = imutils.resize(tmplt, width=ww, inter=cv2.INTER_NEAREST_EXACT)
        paint_tmptl = imutils.resize(paint_tmptl, width=ww, inter=cv2.INTER_NEAREST_EXACT)
        
        # Only 16:9
        # hh, ww = tmplt.shape

        # corrimg = cv2.matchTemplate(img,tmplt,cv2.TM_CCORR_NORMED, mask=tmplt)
        # _, max_val, _, max_loc = cv2.minMaxLoc(corrimg)
        # xx = max_loc[0]
        # yy = max_loc[1]
        
        
        result = img.copy()
        pt1 = (xx,yy)
        pt2 = (xx+ww, yy+hh)

        mask = np.zeros_like(result)
        cv2.rectangle(mask, (pt1[0]+2, pt1[1]+2), (pt2[0]-2, pt2[1]-2), (255, 255, 255), -1)
        result[mask == 0] = 0

        result[pt1[1]:pt2[1], pt1[0]:pt2[0]][paint_tmptl == 255] = 0
        
        # cv2.imwrite('./latest/image.png', img)
        # cv2.imwrite('./latest/template.png', tmplt)
        # cv2.imwrite('./latest/paint.png', paint_tmptl)
        # cv2.imwrite('./latest/hidden.png', result)
        
        # # cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        # # cv2.imshow('image', img)
        # # cv2.namedWindow("template", cv2.WINDOW_NORMAL)
        # # cv2.imshow('template', tmplt)
        
        # cv2.namedWindow("hidden", cv2.WINDOW_NORMAL)
        # cv2.imshow('hidden', result)
        # cv2.waitKey(0)
        
        return result
    
    
    def process_ocr(self):
        print("Taking screenshot...")
                    
        log_path = self.get_window_log()
        self.choice_type = self.get_choice_type(log_path)

        print(self.choice_type)
        if self.choice_type == "nil" or self.choice_type == "Trait":
            return

        window = pwc.getWindowsWithTitle("Roblox")
        if not window:
            return
        
        window_rect = window[0].getClientFrame()
        w, h = window_rect[2] - window_rect[0], window_rect[3] - window_rect[1]
        screenshot = pyautogui.screenshot(region=(window_rect.left, window_rect.top, w, h))
        screenshot = np.array(screenshot)
        
        # window_handle = win32gui.FindWindow(None, "Roblox")
        # window_rect = win32gui.GetClientRect(window_handle)
        # (x, y) = win32gui.ClientToScreen(window_handle, (window_rect[0], window_rect[1]))
        # w, h = window_rect[2] + window_rect[0], window_rect[3] + window_rect[1]
        # screenshot = pyautogui.screenshot(region=(x, y, w, h))
        # screenshot = np.array(screenshot)

        gray = cv2.cvtColor(screenshot.copy(), cv2.COLOR_BGR2GRAY)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        
        # resized_screenshot = imutils.resize(screenshot.copy(), width=1920)
        # resized_screenshot = imutils.resize(screenshot.copy(), width=640)
        
        if w > h:
            resized_screenshot = imutils.resize(screenshot.copy(), width=640)
        else:
            resized_screenshot = imutils.resize(screenshot.copy(), height=640)
        
        results = self.model(resized_screenshot)
        cord = results.xyxyn[0][:, :-1].cpu().numpy()
        
        matches_dict = {}
        
        # test = screenshot.copy()

        if cord.any():
            for i in range(len(cord)):
                row = cord[i]
                if row[4] >= 0.5:
                    x1, y1, x2, y2 = int(row[0] * w), int(row[1] * h), int(row[2] * w), int(row[3] * h)
                    
                    # cv2.rectangle(test, (x1-15, y1-15), (x2+15, y2+25), (0, 255, 0), 2)
                    # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
                    # cv2.imshow('test', test)
                    # cv2.waitKey(0)
                    
                    thresh = cv2.adaptiveThreshold(gray[y1-15:y2+25, x1-15:x2+15], 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
                    thresh = self.extract_text(thresh)
                    thresh = cv2.bitwise_not(thresh)

                    text = pytesseract.image_to_string(
                        thresh, lang="eng", config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
                    )
                    text = text.replace("\n", "")
                    match = self.get_closest_match(text)
                    
                    if not match:
                        continue
                    
                    print(f"{text} | {match['name']}")
                    
                    matches_dict[x1] = match

        sorted_matches = [matches_dict[key] for key in sorted(matches_dict.keys())]
        
        self.addCardsSignal.emit(sorted_matches)
        
        print("Done")
    
    
    def main(self):
        key_pressed = False
        self.loadingSignal.emit(False)
        
        while True:
            if pwc.getActiveWindowTitle() == "Roblox":
                if not key_pressed and (keyboard.is_pressed(self.hotkey1) or (self.hotkey2 and keyboard.is_pressed(self.hotkey2))):
                    key_pressed = True
                    
                    if self.giveFocus:
                        self.helper.activateWindow()
                    
                    if self.helper.data:
                        self.loadingSignal.emit(True)
                        self.process_ocr()
                        self.loadingSignal.emit(False)
                    # else:
                        
                    
                elif key_pressed and not (keyboard.is_pressed(self.hotkey1) or (self.hotkey2 and keyboard.is_pressed(self.hotkey2))):
                    key_pressed = False


if __name__ == '__main__':
    DeepwokenOCR()
