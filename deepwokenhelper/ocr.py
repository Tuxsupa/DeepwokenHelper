import re
import os
import difflib

import cv2
import numpy as np
import pytesseract
import imutils
import keyboard

from ultralytics import YOLO
import ultralytics.utils.torch_utils

import win32gui
import win32ui
import win32con

from PyQt6.QtCore import pyqtSignal, QSettings, QObject
from PyQt6.QtGui import QKeySequence, QWindow


class DeepwokenOCR(QObject):
    addCardsSignal = pyqtSignal(list)
    loadingSignal = pyqtSignal(bool)
    
    def __init__(self, helper):
        super(DeepwokenOCR, self).__init__(helper)
        
        from deepwokenhelper.gui.application import DeepwokenHelper
        self.helper: DeepwokenHelper = helper
        
        pytesseract.pytesseract.tesseract_cmd = r'./tesseract/tesseract'
        
    def fixed_get_cpu_info(self):
        import wmi

        c = wmi.WMI()
        string = c.Win32_Processor()[0].Name
        return string.replace("(R)", "").replace("CPU ", "").replace("@ ", "")
        
    def run(self):
        # Fix for flashing command line with pyinstaller
        ultralytics.utils.torch_utils.get_cpu_info = self.fixed_get_cpu_info
        
        self.model = YOLO('./assets/title_model.onnx', "detect")
        self.model(np.zeros((640, 640, 3), dtype=np.uint8))
        
        self.listener = Listener(self)
        self.listener.start()


    def get_window_log(self):
        log_location = os.environ['LOCALAPPDATA'] + r"\Roblox\logs"
        search_pattern = r"\[FLog::SurfaceController\] \[_:1\]::replaceDataModel: \(stage:0, window = (\S+?)\)"

        files_in_folder = os.listdir(log_location)
        text_files = [file for file in files_in_folder if file.endswith(".log")]
        text_files_sorted = sorted(text_files, key=lambda x: os.path.getmtime(os.path.join(log_location, x)), reverse=True)

        for text_file in text_files_sorted:
            file_path = os.path.join(log_location, text_file)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                match = re.search(search_pattern, content)

                if match:
                    hex_value = match[1]
                    decimal_value = int(hex_value, 16)

                    if self.hwnd == decimal_value:
                        return file_path


    def get_screenshot(self):
        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 8
        titlebar_pixels = 30
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        cropped_x = border_pixels
        cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        # offset_x = window_rect[0] + cropped_x
        # offset_y = window_rect[1] + cropped_y

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (cropped_x, cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[...,:3]
        # img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return np.ascontiguousarray(img)


    def get_choice_type(self, log_path):
        if not log_path:
            return

        with open(log_path, 'r') as file:
            lines = file.readlines()

        reversed_lines = reversed(lines)

        search_pattern = r"\[FLog::Output\] choicetype: (\w+)"
        for line in reversed_lines:
            line = line.strip()
            match = re.search(search_pattern, line)

            if match:
                return match[1]


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
        
        # cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        # cv2.imshow('image', img)
        # cv2.namedWindow("template", cv2.WINDOW_NORMAL)
        # cv2.imshow('template', tmplt)
        
        # cv2.namedWindow("hidden", cv2.WINDOW_NORMAL)
        # cv2.imshow('hidden', result)
        # cv2.waitKey(0)
        
        return result
    
    
    def process_ocr(self):
        print("Taking screenshot...")

        self.hwnd = win32gui.FindWindow(None, "Roblox")
        if not self.hwnd:
            raise Exception('Roblox not found')

        log_path = self.get_window_log()
        self.choice_type = self.get_choice_type(log_path)

        print(self.choice_type)
        if self.choice_type in ["nil", "Trait"]:
            return


        screenshot = self.get_screenshot()
        gray = cv2.cvtColor(screenshot.copy(), cv2.COLOR_RGB2GRAY)

        results = self.model(screenshot, iou=0.5)[0].cpu().numpy()


        matches_dict = {}

        # test = screenshot.copy()

        # cv2.imwrite('./image.png', test)
        # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        # cv2.imshow('test', test)
        # cv2.waitKey(0)

        for box in results.boxes:
            if box.conf[0] >= 0.25:        
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # cv2.rectangle(test, (x1-15, y1-15), (x2+15, y2+25), (0, 255, 0), 2)
                # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
                # cv2.imshow('test', test)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

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


class Listener():
    def __init__(self, ocr: DeepwokenOCR):
        self.ocr = ocr
        ocr.loadingSignal.emit(False)
        
        settings = QSettings("Tuxsuper", "DeepwokenHelper")
        
        self.giveFocus = settings.value("giveFocus", False, bool)
        
        hotkey = settings.value("screenshotHotkey1", QKeySequence("J"), QKeySequence)
        self.hotkey1 = hotkey.toString(QKeySequence.SequenceFormat.NativeText)
        
        hotkey = settings.value("screenshotHotkey2", type=QKeySequence)
        self.hotkey2 = hotkey.toString(QKeySequence.SequenceFormat.NativeText)
        
        self.key_pressed = False
    
    def get_active_window_title(self):
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    
    def on_press(self, _):
        if not self.key_pressed and self.get_active_window_title() == "Roblox":
            self.key_pressed = True
            
            if self.giveFocus:
                self.ocr.helper.windowHandle().setVisibility(QWindow.Visibility.Windowed)

            if self.ocr.helper.data:
                self.ocr.loadingSignal.emit(True)
                self.ocr.process_ocr()
                self.ocr.loadingSignal.emit(False)
    
    def on_release(self, _):
        self.key_pressed = False
    
    def start(self):
        if self.hotkey1:
            keyboard.on_press_key(self.hotkey1, self.on_press)
            keyboard.on_release_key(self.hotkey1, self.on_release)
            
        if self.hotkey2:
            keyboard.on_press_key(self.hotkey2, self.on_press)
            keyboard.on_release_key(self.hotkey2, self.on_release)