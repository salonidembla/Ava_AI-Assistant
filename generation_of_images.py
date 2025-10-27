import requests, json, os, time, webbrowser, pathlib

def read_config():
    try:
        with open("config/config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("[ImageGen] ⚠️ Could not read config:", e)
        return {}

def generate_images(prompt):
    cfg = read_config()
    base_url = cfg.get("Img_Gen_Colab")
    if not base_url:
        print("[ImageGen] ❌ No Img_Gen_Colab URL found in config.json")
        return []

    endpoint = base_url.rstrip("/") + "/generate"
    payload = {"prompt": prompt}

    print(f"[ImageGen] 🎨 Sending prompt to Colab: {prompt}")
    try:
        resp = requests.post(endpoint, json=payload, timeout=120)
        if resp.status_code == 200:
            os.makedirs("output", exist_ok=True)
            filename = f"img_{int(time.time())}.png"
            out_path = os.path.join("output", filename)
            with open(out_path, "wb") as f:
                f.write(resp.content)
            print(f"[ImageGen] ✅ Saved image as {out_path}")
            return [filename]
        else:
            print(f"[ImageGen] ⚠️ Error: {resp.status_code} {resp.text}")
            return []
    except Exception as e:
        print("[ImageGen] ❌ Exception:", e)
        return []

class ShowImage:
    def __init__(self, folder_path, files):
        self.folder_path = folder_path
        self.files = files

    def open(self, index=0):
        if not self.files:
            print("[ImageGen] ⚠️ No images found.")
            return
        img_path = os.path.join(self.folder_path, self.files[index])
        if os.path.exists(img_path):
            print(f"[ImageGen] 🖼️ Opening {img_path}")
            if os.name == "nt":  # Windows
                os.startfile(img_path)
            else:
                webbrowser.open(pathlib.Path(img_path).absolute().as_uri())
        else:
            print("[ImageGen] ❌ Image not found:", img_path)
