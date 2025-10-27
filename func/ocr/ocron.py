import json
import io
import requests
from PIL import ImageGrab
import pyautogui as pag
from time import sleep, time
import traceback

def load_ocr_url():
    """Load OCR endpoint URL from config/config.json"""
    try:
        with open("config/config.json") as f:
            config = json.load(f)
            url = config.get("OCR_Colab", "")
            if not url:
                raise ValueError("OCR_Colab URL missing in config file.")
            return url
    except Exception as e:
        print(f"[OCR] ❌ Config error: {e}")
        return None


def ocr_click(search_string: str, double_click=False):
    """
    Capture the screen, send to OCR API, find button with `search_string`,
    and click it automatically.

    Args:
        search_string (str): Text to locate on screen.
        double_click (bool): Whether to double click instead of single click.
    """
    url = load_ocr_url()
    if not url:
        print("[OCR] ❌ No OCR URL configured in config.json")
        return "No OCR URL configured."

    try:
        print(f"[OCR] 📸 Capturing screen for '{search_string}'...")
        screenshot = ImageGrab.grab()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        payload = {
            "search_string": search_string,
            "double_click": "on" if double_click else "off"
        }
        files = {"image": img_bytes}

        print("[OCR] 🚀 Sending to remote OCR endpoint...")
        response = requests.post(url, files=files, data=payload, timeout=120)

        if response.status_code != 200:
            print(f"[OCR] ⚠️ HTTP {response.status_code}: {response.text}")
            return f"HTTP Error {response.status_code}"

        result = response.json()
        if "error" in result:
            print(f"[OCR] ❌ API error: {result['error']}")
            return result["error"]

        point = result.get("point")
        if not point or len(point) < 2:
            print("[OCR] ❌ No click coordinates returned.")
            return "No coordinates found."

        x, y = point
        print(f"[OCR] ✅ Found '{search_string}' at {x}, {y}")

        # Safety pause to avoid accidental misclicks
        sleep(0.5)
        pag.moveTo(x, y, duration=0.3)

        if double_click:
            pag.click(x, y, clicks=2, interval=0.25)
        else:
            pag.click(x, y)

        print(f"[OCR] 🖱️ Clicked successfully at ({x}, {y})")
        return f"Clicked '{search_string}' successfully."

    except Exception as e:
        print("[OCR] ❌ Exception during OCR click:", e)
        traceback.print_exc()
        return f"OCR click failed: {e}"
