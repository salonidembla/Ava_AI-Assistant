import cv2
import requests
import json
import time

cache = {}

def url():
    try:
        if 'url' in cache and cache['url'][1] > time.time():
            return cache['url'][0]

        with open('config/config.json') as config_file:
            config = json.load(config_file)
            url = config.get('Img_Detection_Colab')
            if url:
                cache['url'] = url, time.time() + 3600
                return url
            else:
                return None
    except Exception as e:
        print(f"[ObjectDetect] Config error: {e}")
        return None


def capture_and_send_image():
    api_url = url()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ObjectDetect] Failed to open camera.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("[ObjectDetect] Failed to capture frame.")
        return

    # 🧠 If remote URL exists, use it
    if api_url:
        try:
            _, img_encoded = cv2.imencode(".jpg", frame)
            files = {'file': img_encoded.tobytes()}
            response = requests.post(api_url, files=files)
            if response.status_code == 200:
                result = response.json()
                detections = result.get('detections', [])
                if detections and isinstance(detections[0], list):
                    object_names = [obj['name'] for obj in detections[0]
                                    if obj.get('confidence', 0) > 0.5]
                    print("[ObjectDetect] Detected objects:", object_names)
                    return object_names
            else:
                print("[ObjectDetect] HTTP error:", response.status_code, response.text)
        except Exception as e:
            print("[ObjectDetect] Remote request failed:", e)

    # 🧠 Fallback to local OpenCV detection if no remote endpoint
    print("[ObjectDetect] 🧩 Running local object detection fallback...")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    print(f"[ObjectDetect] 🧠 Local detection found {len(faces)} faces.")
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imshow("Detected Objects (Local)", frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
    return [f"faces_detected={len(faces)}"]
