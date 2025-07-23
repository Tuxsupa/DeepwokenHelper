import re
import os
import threading
import logging
import contextlib


import cv2
import numpy as np
import pytesseract
import imutils
from pynput import keyboard
from thefuzz import fuzz
import onnxruntime as ort
from windows_capture import WindowsCapture, Frame, InternalCaptureControl

import win32gui
import win32ui
import win32con

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QKeySequence, QWindow


from deepwokenhelper.gui.control_panel import ScreenshotMethod


logger = logging.getLogger("helper")


class DeepwokenOCR(QObject):
    addCardsSignal = pyqtSignal(list)
    processSignal = pyqtSignal()

    def __init__(self, helper):
        super(DeepwokenOCR, self).__init__()

        from deepwokenhelper.gui.application import DeepwokenHelper

        self.helper: DeepwokenHelper = helper
        self.hotkeys = None

        self.processSignal.connect(self.process_ocr)

        self.tesseract_lock = threading.Lock()

        self.tmplt = cv2.imread("./assets/banner-mask.png", cv2.IMREAD_GRAYSCALE)
        self.paint_tmplt = cv2.imread("./assets/paint-mask.png", cv2.IMREAD_GRAYSCALE)

        pytesseract.pytesseract.tesseract_cmd = r"./tesseract/tesseract"

    def start(self):
        self.helper.start_loading_signal.emit("Initiating YOLO Model...")

        self.model = YOLOModel("./assets/deepwoken-yolov11n-nms.onnx", conf_thres=0.25)

        self.hotkeys = Hotkeys(self)

        self.helper.stop_loading_signal.emit()

    def get_window_log(self):
        log_location = os.environ["LOCALAPPDATA"] + r"\Roblox\logs"
        search_pattern = r"\[FLog::SurfaceController\] \[_:1\]::replaceDataModel: \(stage:0, window = (\S+?)\)"

        files_in_folder = os.listdir(log_location)
        text_files = [file for file in files_in_folder if file.endswith(".log")]
        text_files_sorted = sorted(
            text_files,
            key=lambda x: os.path.getmtime(os.path.join(log_location, x)),
            reverse=True,
        )

        for text_file in text_files_sorted:
            file_path = os.path.join(log_location, text_file)

            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                match = re.search(search_pattern, content)

                if match:
                    hex_value = match[1]
                    decimal_value = int(hex_value, 16)

                    if self.hwnd == decimal_value:
                        return file_path

    def get_choice_type(self, log_path):
        if not log_path:
            return

        with open(log_path, "r") as file:
            lines = file.readlines()

        reversed_lines = reversed(lines)

        # search_pattern = r"\[FLog::Output\] choicetype: (\w+)"
        # search_pattern = r"\[PROGRESSION\] choiceType: (\w+), pointType: (\w+), choices: (\w+)"
        search_pattern = r"\[PROGRESSION\] choiceType: (\w+)"  # choiceType: Talent, pointType: Focused, choices: 5
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

        elif self.choice_type == "Trait":  # Skipped
            return self.helper.data.traits

        return self.helper.data.all_cards

    def get_closest_match(self, target_string):
        max_similarity = 0
        closest_match = None

        for card_key, card in self.get_type_card().items():
            card_name = card.get("name") or card_key
            card_name = re.sub(r" \[[A-Za-z]{3}\]", "", card_name).lower()

            similarity = fuzz.ratio(target_string, card_name)

            if similarity >= 50:
                if similarity > max_similarity:
                    max_similarity = similarity
                    closest_match = card

        return closest_match

    def extract_text(self, img):
        best_max_val = 0
        best_max_loc = None
        best_tmplt_size = None

        for idx in range(50):
            scaled_tmplt = imutils.resize(
                self.tmplt.copy(),
                width=img.shape[1] - idx,
                inter=cv2.INTER_NEAREST_EXACT,
            )

            corrimg = cv2.matchTemplate(
                img,
                scaled_tmplt,
                cv2.TM_CCORR_NORMED,
                mask=scaled_tmplt,
            )
            _, max_val, _, max_loc = cv2.minMaxLoc(corrimg)

            if max_val > best_max_val:
                best_max_val = max_val
                best_max_loc = max_loc
                best_tmplt_size = scaled_tmplt.shape[::-1]

        ww, hh = best_tmplt_size
        xx, yy = best_max_loc

        # tmplt = imutils.resize(
        #     self.tmplt.copy(), width=ww, inter=cv2.INTER_NEAREST_EXACT
        # )
        paint_tmplt = imutils.resize(
            self.paint_tmplt.copy(), width=ww, inter=cv2.INTER_NEAREST_EXACT
        )

        # Only 16:9
        # hh, ww = tmplt.shape

        # corrimg = cv2.matchTemplate(img,tmplt,cv2.TM_CCORR_NORMED, mask=tmplt)
        # _, max_val, _, max_loc = cv2.minMaxLoc(corrimg)
        # xx = max_loc[0]
        # yy = max_loc[1]

        result = img.copy()
        pt1 = (xx, yy)
        pt2 = (xx + ww, yy + hh)

        mask = np.zeros_like(result)
        cv2.rectangle(
            mask,
            (pt1[0] + 2, pt1[1] + 2),
            (pt2[0] - 2, pt2[1] - 2),
            (255, 255, 255),
            -1,
        )
        result[mask == 0] = 0

        result[pt1[1] : pt2[1], pt1[0] : pt2[0]][paint_tmplt == 255] = 0

        # cv2.imwrite('./latest/image.png', img)
        # cv2.imwrite('./latest/template.png', tmplt)
        # cv2.imwrite('./latest/paint.png', paint_tmplt)
        # cv2.imwrite('./latest/hidden.png', result)

        # cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        # cv2.imshow("image", img)
        # cv2.namedWindow("template", cv2.WINDOW_NORMAL)
        # cv2.imshow("template", tmplt)

        # cv2.namedWindow("hidden", cv2.WINDOW_NORMAL)
        # cv2.imshow("hidden", result)
        # cv2.waitKey(0)

        return result

    @pyqtSlot()
    def process_ocr(self):
        logger.info("Taking screenshot...")
        self.helper.start_loading_signal.emit("Processing screenshot...")

        self.hwnd = win32gui.FindWindow(None, "Roblox")
        if not self.hwnd:
            self.helper.stop_loading_signal.emit()
            self.helper.errorSignal.emit("Roblox window not found.")
            raise Exception("Roblox not found")

        self.log_path = self.get_window_log()
        self.choice_type = self.get_choice_type(self.log_path)

        logger.info(self.choice_type)
        if self.choice_type in ["Trait"]:
            # TODO: "nil" needed for extra hands but might give out errors with other hands that also give out "nil"
            self.helper.stop_loading_signal.emit()
            return

        screenshot = Screenshot(self).get_screenshot()
        gray = cv2.cvtColor(screenshot.copy(), cv2.COLOR_RGB2GRAY)

        results = self.model.predict(screenshot)

        matches_dict = {}

        # test = screenshot.copy()

        # cv2.imwrite("./image.png", test)
        # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        # cv2.imshow("test", test)
        # cv2.waitKey(0)

        # for box in results.boxes:
        for box in results:
            # x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1, y1, x2, y2 = map(int, box[:4])

            # cv2.rectangle(test, (x1 - 15, y1 - 15), (x2 + 15, y2 + 25), (0, 255, 0), 2)

            # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
            # cv2.imshow("test", test)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            thresh = cv2.adaptiveThreshold(
                gray[y1 - 15 : y2 + 25, x1 - 15 : x2 + 15],
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY_INV,
                7,
                7,
            )
            thresh = self.extract_text(thresh)
            thresh = cv2.bitwise_not(thresh)

            with self.tesseract_lock:
                text: str = pytesseract.image_to_string(
                    thresh,
                    lang="eng",
                    config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ",
                )
            text = text.replace("\n", "")
            match = self.get_closest_match(text)

            if not match:
                logger.info(f"{text} | None")
                continue

            logger.info(f"{text} | {match['name']}")

            matches_dict[x1] = match

        # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        # cv2.imshow("test", test)
        # cv2.waitKey(0)

        sorted_matches = [matches_dict[key] for key in sorted(matches_dict.keys())]

        self.addCardsSignal.emit(sorted_matches)

        logger.info("Done processing cards.")
        self.helper.stop_loading_signal.emit()


class YOLOModel:
    def __init__(self, model_path: str, conf_thres: float = 0.25):
        # from ultralytics.utils import torch_utils

        # # Fix for flashing command line with pyinstaller
        # torch_utils.get_cpu_info = self.fixed_get_cpu_info

        # self.model = YOLO(model_path)
        # self.model(np.zeros((640, 640, 3), dtype=np.uint8))

        self.model = ort.InferenceSession(model_path)
        self.conf_thres = conf_thres

    def predict(self, img: np.ndarray):
        tensor = self.preprocess(img)
        results = self.inference(tensor)
        results = self.postprocess(results, img.shape[:2])
        return results

    def preprocess(self, img: np.ndarray):
        tensor = self.letterbox(img)
        tensor = tensor.transpose(2, 0, 1)
        tensor = np.expand_dims(tensor, axis=0)
        tensor = np.ascontiguousarray(tensor)
        tensor = tensor.astype(np.float32) / 255.0
        return tensor

    def inference(self, tensor: np.ndarray):
        # results = self.model(img, iou=0.5)[0].cpu().numpy()

        results = self.model.run(None, {"images": tensor})
        return results[0][0]

    def postprocess(self, results, img_shape):
        results = results[results[:, 4] >= self.conf_thres, :5]

        results[:, :4] = self.scale_boxes((640, 640), results[:, :4], img_shape)
        return results

    def scale_boxes(self, img1_shape, boxes, img0_shape):
        """
        Rescale bounding boxes from one image shape to another.

        Rescales bounding boxes from img1_shape to img0_shape, accounting for padding and aspect ratio changes.
        """
        gain = min(
            img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1]
        )  # gain  = old / new
        pad = (
            round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1),
            round((img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1),
        )  # wh padding

        boxes[..., 0] -= pad[0]  # x padding
        boxes[..., 1] -= pad[1]  # y padding
        boxes[..., 2] -= pad[0]  # x padding
        boxes[..., 3] -= pad[1]  # y padding

        boxes[..., :4] /= gain
        return self.clip_boxes(boxes, img0_shape)

    def clip_boxes(self, boxes, shape):
        """Clip bounding boxes to image boundaries."""
        boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2
        return boxes

    def letterbox(self, im: np.ndarray, new_shape=(640, 640)):
        # Resize and pad image while meeting stride constraints
        shape = im.shape[:2]  # current shape [height, width]

        # Calculate ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        # Compute new_unpad dimensions (maintain aspect ratio)
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))

        # Compute padding dimensions
        dw = new_shape[1] - new_unpad[0]  # width padding
        dh = new_shape[0] - new_unpad[1]  # height padding

        # Divide padding equally on both sides
        dw /= 2
        dh /= 2

        # Resize image
        if shape[::-1] != new_unpad:
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)

        # Create letterboxed image
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(
            im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )

        # return im, r, (dw, dh)
        return im


class Hotkeys:
    def __init__(self, ocr: DeepwokenOCR):
        self.ocr = ocr
        self.listener = None

        settings = self.ocr.helper.settings

        self.giveFocus = settings.value("giveFocus", False, bool)

        hotkey1 = settings.value("screenshotHotkey1", QKeySequence("J"), QKeySequence)
        hotkey2 = settings.value("screenshotHotkey2", type=QKeySequence)

        self.start_listener(hotkey1, hotkey2)

    def start_listener(self, hotkey1, hotkey2):
        hotkey1 = self.get_fixed_hotkey(hotkey1)
        hotkey2 = self.get_fixed_hotkey(hotkey2)

        hotkeys = {hotkey1: self.on_activate, hotkey2: self.on_activate}
        hotkeys = self.remove_empty_hotkeys(hotkeys)

        if self.listener:
            self.listener.stop()

        self.listener = keyboard.GlobalHotKeys(hotkeys)
        self.listener.start()

    def remove_empty_hotkeys(self, hotkeys):
        keys_to_remove = [key for key, _ in hotkeys.items() if key == ""]
        for key in keys_to_remove:
            del hotkeys[key]

        return hotkeys

    def get_fixed_hotkey(self, hotkey: QKeySequence):
        hotkey: str = hotkey.toString(QKeySequence.SequenceFormat.NativeText).lower()

        return (
            hotkey.replace("ctrl", "<ctrl>")
            .replace("shift", "<shift>")
            .replace("alt", "<alt>")
            .replace("cmd", "<cmd>")
        )

    def get_active_window_title(self):
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)

    def on_activate(self):
        logger.info("Global hotkey activated!")

        if self.get_active_window_title() == "Roblox":
            if self.giveFocus:
                self.ocr.helper.windowHandle().setVisibility(
                    QWindow.Visibility.Windowed
                )

            if self.ocr.helper.data:
                self.ocr.processSignal.emit()


class Screenshot:
    def __init__(self, ocr: DeepwokenOCR):
        self.ocr = ocr

        self.hwnd = ocr.hwnd
        self.frame_event = threading.Event()

        settings = ocr.helper.settings

        self.screenshot_method = settings.value(
            "screenshotMethod", ScreenshotMethod.AUTOMATIC, ScreenshotMethod
        )

        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.client_rect = win32gui.GetClientRect(self.hwnd)

        self.border_width = (window_rect[2] - window_rect[0] - self.client_rect[2]) // 2
        self.titlebar_height = (
            window_rect[3] - window_rect[1] - self.client_rect[3] - self.border_width
        )

    def wgc_method(self):
        capture = WindowsCapture(cursor_capture=False, window_name="Roblox")
        self.captured_frame = None

        @capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            if self.captured_frame is not None:
                return

            captured_frame = frame.frame_buffer.copy()
            self.captured_frame = captured_frame[self.titlebar_height :, :]

            self.frame_event.set()

            capture_control.stop()

        @capture.event
        def on_closed():
            print("Capture Session Closed")

        capture.start_free_threaded()
        self.frame_event.wait(5)

        img = self.captured_frame[..., :3]

        return img

    def bitblt_method(self):
        with contextlib.suppress(Exception):
            from ctypes import windll

            windll.user32.SetProcessDPIAware()

        w = self.client_rect[2]
        h = self.client_rect[3]
        cropped_x = self.border_width
        cropped_y = self.titlebar_height

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (w, h), dcObj, (cropped_x, cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        # dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.frombuffer(signedIntsArray, dtype="uint8")
        img.shape = (h, w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        img = img[..., :3]
        # img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return np.ascontiguousarray(img)

    def get_renderer(self, log_path):
        if not log_path:
            return

        with open(log_path, "r") as file:
            lines = file.readlines()

        search_pattern = r"FFlagDebugGraphicsPrefer(\w+)"
        for line in lines:
            line = line.strip()
            match = re.search(search_pattern, line)

            if match:
                return match[1].replace("FFlagDebugGraphicsPrefer", "")

    def is_image_white(self, img: np.ndarray):
        return False if img.size == 0 else np.all(img == 255)

    def get_screenshot(self):
        if self.screenshot_method == ScreenshotMethod.AUTOMATIC:
            renderer = self.get_renderer(self.ocr.log_path)

            if renderer in ("Vulkan", "OpenGL"):
                logger.info("Using WGC screenshot method.")
                screenshot = self.wgc_method()
            else:
                logger.info("Using BitBlt screenshot method.")
                screenshot = self.bitblt_method()
                if self.is_image_white(screenshot):
                    logger.warning("BitBlt returned a white image, switching to WGC.")
                    screenshot = self.wgc_method()

        elif self.screenshot_method == ScreenshotMethod.BITBLT:
            logger.info("Using BitBlt screenshot method.")
            screenshot = self.bitblt_method()

        elif self.screenshot_method == ScreenshotMethod.WGC:
            logger.info("Using WGC screenshot method.")
            screenshot = self.wgc_method()

        # cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        # cv2.imshow("test", screenshot)
        # cv2.waitKey(0)

        return screenshot
