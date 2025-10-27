
Ava – AI Voice Assistant

Ava is an intelligent, desktop-based voice assistant built with Python and PyQt5. It integrates conversational AI (Google Gemini), Colab-hosted Stable Diffusion for image generation, Colab-hosted OCR for on-screen text detection and automation, PowerPoint generation, task management, object detection, and speech synthesis. The project supports both voice and text-based interaction through a modern graphical interface.

---

## Key Features

1. Conversational AI

   * Powered by Google Gemini (gemini-2.5-flash) via the google-generativeai SDK.
   * Handles general queries, performs Wikipedia lookups, and provides detailed responses.

2. Voice and Text Interaction

   * Supports microphone input and on-screen text entry.
   * Responses are displayed on the GUI and can be spoken aloud using the included TTS modules.

3. Image Generation (Colab)

   * Generates high-quality images through a Stable Diffusion endpoint hosted on Google Colab (Flask + ngrok).
   * The GUI sends POST requests to the Colab /generate endpoint and displays downloaded results.

4. OCR-Based Automation (Colab)

   * Screen capture is sent to a Colab-hosted OCR service (Flask + ngrok) which returns detected text and coordinates.
   * OCR is used to locate on-screen text and perform automated clicks via pyautogui.
   * OCR Colab must be run and its public /ocr endpoint configured in the local config.

5. PowerPoint Generation

   * Automatically generates structured presentations based on a given topic and saves .pptx files.

6. Object Detection

   * Activates the webcam for local object/face detection.

7. Task Management System

   * Add, view, and delete tasks using natural commands; tasks are stored in todo.txt.

8. System Automation

   * Open desktop applications, take screenshots, show time/date, and issue notifications.

---

## Folder Structure

AVA-main/
│
├── ava_main.py                 Main application entry point (GUI + core glue)
├── config/
│   └── config.json             Local configuration (API keys and service URLs) - NOT included in repo
│
├── func/
│   ├── basic/
│   │   └── listenpy.py         Microphone input handling
│   ├── speak/
│   │   ├── speakon.py          Primary TTS (used by GUI)
│   │   └── speakmid.py         Alternate TTS helper (gTTS + pygame)
│   ├── ocr/
│   │   └── ocron.py            Local client wrapper that sends screenshots to OCR Colab /ocr endpoint
│   ├── OF/
│   │   ├── obj_detect.py       Object detection module
│   │   └── dataonline.py       (Optional) web search integration (can be removed)
│   └── Powerpointer/
│       └── main.py             PowerPoint generator
│
├── llm/
│   └── chatgpt.py              Gemini integration for conversational AI
│
├── generation_of_images.py     Image-generation client (calls Colab /generate endpoint)
├── todo.txt                    Local task storage
├── requirements.txt            Python dependencies
├── README.md                   Documentation (this file)
└── venv/                       Virtual environment (excluded from Git)

---

## Configuration File (REQUIRED)

Create config/config.json. This file is not included in the repository and must be created locally.

Required fields (example):

{
"GEMINI_API": "YOUR_GEMINI_API_KEY",
"COLAB_IMAGE_URL": "https://<your-colab-ngrok>/generate",
"COLAB_OCR_URL": "https://<your-colab-ngrok>/ocr"
}

Notes:

* GEMINI_API is your Google Gemini API key. The project reads this key from config/config.json (and some modules fall back to environment variables if present).
* COLAB_IMAGE_URL must point to the public Colab Flask endpoint that accepts POST requests for image generation.
* COLAB_OCR_URL must point to the public Colab Flask endpoint that accepts POST requests for OCR (image file + search_string) and returns JSON { "point": [x, y], ... }.
* Do NOT commit config/config.json. Add it to .gitignore.

---

## Colab Setup (Image Generation)

1. In your image Colab notebook:

   * Load the Stable Diffusion pipeline and move it to GPU if available.
   * Install and configure ngrok (set auth token).
   * Start a Flask app with an endpoint /generate that accepts POST with JSON {"prompt": "..."} and returns an image file.
   * Run all cells and copy the public ngrok URL (example: [https://abcd1234.ngrok-free.app/generate](https://abcd1234.ngrok-free.app/generate)).

2. Place that URL into config/config.json as COLAB_IMAGE_URL.

3. Keep the Colab notebook running (do not disconnect) while using the GUI image-generation feature.

Example POST usage (client side):

* POST COLAB_IMAGE_URL with JSON { "prompt": "a golden retriever" }
* Colab returns a generated PNG file.

---

## Colab Setup (OCR Server)

1. In your OCR Colab notebook:

   * Install EasyOCR and necessary libraries.
   * Create a Flask endpoint /ocr that accepts multipart form data with an image file plus form fields:

     * search_string (the text to look for)
     * double_click (optional)
   * The endpoint should run OCR on the image to find bounding boxes, match search_string, compute click coordinates, and return JSON:
     { "point": [x, y], "text": "found text", "confidence": 0.93 }
   * Start ngrok to expose the Flask server and copy the public ngrok URL (example: [https://wxyz5678.ngrok-free.app/ocr](https://wxyz5678.ngrok-free.app/ocr)).

2. Place that URL into config/config.json as COLAB_OCR_URL.

3. Keep the Colab OCR runtime active while using OCR features.

Notes on ngrok:

* Free ngrok sessions expire when the Colab runtime disconnects. Re-run the ngrok cell and update the URL in config/config.json when necessary.
* Consider using a persistent remote server if you need a long-lived public endpoint.

---

## Setup Instructions

1. Clone the Repository
   git clone [https://github.com/salonidembla/ava-ai-assistant.git](https://github.com/salonidembla/ava-ai-assistant.git)
   cd ava-ai-assistant

2. Create a Virtual Environment
   python -m venv venv

3. Activate the Environment
   Windows:
   venv\Scripts\activate
   macOS/Linux:
   source venv/bin/activate

4. Upgrade pip
   python -m pip install --upgrade pip

5. Install Dependencies
   pip install -r requirements.txt

If specific packages fail to install (platform issues), refer to the Troubleshooting section below.

6. Create config/config.json as shown in the Configuration File section.

7. If you plan to use Colab image or OCR endpoints, run the Colab notebooks to obtain public URLs and add them to config/config.json.

8. Run the application
   python ava_main.py

The GUI opens and greets you. Enter commands or use the voice input button.


## Supported Voice Commands

"What is the time?"                Announces the current time
"What is the date today?"          Reads and displays date
"Generate image of a beach sunset" Generates image via Colab
"Create PowerPoint on climate change" Builds a presentation
"New task complete the report"     Adds to todo.txt
"Show work"                        Reads tasks from file
"Delete task complete the report"  Deletes specific task
"Open Chrome"                      Launches Chrome
"Take screenshot"                  Saves screenshot locally
"Wikipedia Artificial Intelligence" Retrieves summary
"Send email"                       Sends predefined test email
"Detect"                           Starts camera for object detection
"Exit"                             Closes Ava gracefully

---

## Dependencies

The project depends on the following core libraries:

PyQt5
google-generativeai
requests
pygame
gTTS
playsound
pillow
pyautogui
pywhatkit
wikipedia
flask
torch
diffusers
opencv-python
python-pptx
plyer
easyocr
keyboard
pyngrok

Install using:
pip install -r requirements.txt

---

## License

This project is distributed under the MIT License.
You are free to modify, use, and distribute the code with appropriate credit.

---

## Author

Developed by: Saloni Dembla
Year: 2025

