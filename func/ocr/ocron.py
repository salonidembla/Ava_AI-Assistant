def ocr_click(search_string: str, double_click=False):
    """
    Capture the screen, send to OCR API, and click directly at the returned coordinates.
    No confirmation checks — clicks whatever the OCR server detects.
    """
    import json, io, requests, traceback
    from PIL import ImageGrab, ImageDraw
    import pyautogui as pag
    from time import sleep, time
    import platform

    # Enable DPI awareness (Windows)
    if platform.system() == "Windows":
        try:
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except Exception:
                ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    # Load OCR URL
    try:
        with open("config/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
            url = config.get("OCR_Colab", "")
            if not url:
                raise ValueError("OCR_Colab URL missing in config file.")
    except Exception as e:
        print(f"[OCR] ❌ Config error: {e}")
        return None

    try:
        print(f"[OCR] 📸 Capturing screen for '{search_string}'...")
        screenshot = ImageGrab.grab()
        img_bytes = io.BytesIO()
        screenshot.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        payload = {"search_string": search_string}
        files = {"image": img_bytes}

        print("[OCR] 🚀 Sending to remote OCR endpoint...")
        response = requests.post(url, files=files, data=payload, timeout=120)

        if response.status_code != 200:
            print(f"[OCR] ⚠️ HTTP {response.status_code}: {response.text}")
            return

        result = response.json()
        print("[OCR] ✅ Server response:", result)

        point = result.get("point")
        if not point or len(point) < 2:
            print("[OCR] ❌ No coordinates returned.")
            return

        # Get coordinates
        x, y = float(point[0]), float(point[1])

        # Adjust for scaling if needed
        screen_w, screen_h = pag.size()
        img_w, img_h = screenshot.size
        if (img_w != screen_w) or (img_h != screen_h):
            scale_x = screen_w / img_w
            scale_y = screen_h / img_h
            x, y = x * scale_x, y * scale_y

        # Optional debug image
        try:
            dbg = screenshot.copy()
            draw = ImageDraw.Draw(dbg)
            r = 10
            draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=4)
            dbg.save("ocr_debug_image.png")
            print("[OCR] 🖼️ Saved debug image to ocr_debug_image.png")
        except Exception:
            pass

        # Click immediately
        sleep(0.2)
        pag.moveTo(x, y, duration=0.2)
        if double_click:
            pag.click(x, y, clicks=2, interval=0.25)
        else:
            pag.click(x, y)

        print(f"[OCR] 🖱️ Clicked successfully at ({x}, {y})")

    except Exception as e:
        print("[OCR] ❌ Error:", e)
        traceback.print_exc()
