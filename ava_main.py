import sys, os, json, datetime, pyautogui, webbrowser, smtplib, wikipedia
from email.message import EmailMessage
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QTextBrowser,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import QTimer, Qt
from func.basic.listenpy import Listen

from func.speak.speakmid import mid as off
from func.OF.obj_detect import capture_and_send_image
from func.Powerpointer.main import generate_powerpoint
from func.ocr.ocron import ocr_click
from generation_of_images import generate_images, ShowImage
from llm.chatgpt import ChatGpt


# ==================== CONFIG ====================
with open("config/config.json") as f:
    CONFIG = json.load(f)
print("[Config] ✅ Loaded Gemini API key")


# ==================== EMAIL ====================
def send_email_smtp(sender_email, app_password, to_email, subject, body):
    try:
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = sender_email, to_email, subject
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return True, f"✅ Email sent to {to_email}"
    except Exception as e:
        return False, f"❌ Email failed: {e}"


# ==================== CORE ====================
class AvaCore:
    """Handles backend logic for all Ava commands."""

    def handle_query(self, query):
        query = query.lower().strip()
        print(f"[User]: {query}")

        if any(k in query for k in ["exit", "quit", "close"]):
            return "Goodbye!"

        # --- DATE / TIME ---
        elif "time" in query:
            now = datetime.datetime.now().strftime("%I:%M %p")
            return f"Current time is {now}"

        elif "date" in query:
            today = datetime.datetime.now().strftime("%A, %d %B %Y")
            return f"Today is {today}"

        # --- SCREENSHOT ---
        elif "screenshot" in query:
            fname = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot().save(fname)
            return f"Screenshot saved as {fname}"

        # --- IMAGE GENERATION ---
        elif "generate image" in query:
            prompt = query.replace("generate image", "").strip()
            if not prompt:
                return "Please tell me what image to generate."
            
            # Announce before generation
            print("[Ava] Generating image...")
            off(f"Generating image for {prompt}")
            
            imgs = generate_images(prompt)
            if imgs:
                viewer = ShowImage("output", imgs)
                viewer.open(0)
                off("Image generated successfully.")
                return f"Image generated successfully for '{prompt}'."
            else:
                off("Failed to generate image.")
                return "Failed to generate image."


        # --- POWERPOINT ---
        elif "powerpoint" in query or "presentation" in query:
            topic = query.replace("create", "").replace("powerpoint", "").replace("presentation", "").strip()
            if not topic:
                return "Please tell me the topic for PowerPoint."

            # Announce before creating
            print("[Ava] Creating PowerPoint...")
            off(f"Creating PowerPoint on {topic}")

            ppt = generate_powerpoint(topic)
            if ppt and os.path.exists(ppt):
                off("Presentation created successfully.")
                os.startfile(ppt)
                return f"Presentation created successfully on '{topic}'."
            else:
                off("Failed to create presentation.")
                return "Failed to create presentation."


        # --- OCR ---
        elif "click" in query:
            print("[Ava] Processing OCR click...")
            off("Processing OCR click...")
            try:
                # Extract the text to click after the word "click"
                target = query.replace("click", "").strip()
                if not target:
                    off("Please specify what to click.")
                    return "Please specify what to click."

                print(f"[Ava] OCR will search for: '{target}'")
                result = ocr_click(target)  # ✅ Now uses the user's actual target
                off("OCR click completed.")
                return result
            except Exception as e:
                off("OCR failed.")
                return f"OCR failed: {e}"



        # --- OBJECT DETECTION ---
        elif "detect" in query or "camera" in query:
            print("[Ava] Opening camera for object detection...")
            off("Opening camera for object detection...")
            capture_and_send_image()
            off("Camera stream active.")
            return "Object detection completed."


        # --- TASK MANAGEMENT ---
        elif "new task" in query:
            task = query.replace("new task", "").strip()
            if not task:
                return "Please tell me the task to add."
            with open("todo.txt", "a", encoding="utf-8") as f:
                f.write(task + "\n")
            return f"Added task: {task}"

        elif "show work" in query:
            try:
                with open("todo.txt", "r", encoding="utf-8") as f:
                    tasks = f.read().strip()
                return tasks if tasks else "No tasks found."
            except FileNotFoundError:
                return "No tasks file found."

        elif "delete task" in query:
            task = query.replace("delete task", "").strip()
            try:
                with open("todo.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open("todo.txt", "w", encoding="utf-8") as f:
                    for line in lines:
                        if task.lower() not in line.lower():
                            f.write(line)
                return f"Deleted task: {task}"
            except Exception as e:
                return f"Error deleting task: {e}"

        # --- EMAIL ---
        elif "send email" in query or "send gmail" in query:
            try:
                sender = "salonidembla2004@gmail.com"
                app_pass = CONFIG.get("gmailpass", "")
                recipient = "salonidembla57@gmail.com"  # You can later make this dynamic if needed

                if not app_pass:
                    off("Gmail password not found in config.")
                    return "❌ Gmail app password missing in config.json."

                # Step 1: Ask for subject
                off("What should be the subject of the email?")
                subject = Listen().strip()
                if not subject:
                    return "No subject received. Email cancelled."

                off(f"You said, {subject}. Got it.")

                # Step 2: Ask for message
                off("What should I write in the email?")
                body = Listen().strip()
                if not body:
                    return "No message received. Email cancelled."

                off(f"Composing email to {recipient} with subject {subject}.")
                print(f"[Email] From: {sender}\nTo: {recipient}\nSubject: {subject}\nBody: {body}")

                # Step 3: Send email
                ok, msg = send_email_smtp(sender, app_pass, recipient, subject, body)

                if ok:
                    off("Email sent successfully.")
                else:
                    off("Failed to send email.")
                return msg

            except Exception as e:
                off("Something went wrong while sending the email.")
                return f"Email sending failed: {e}"


        # --- WIKIPEDIA ---
        elif "wikipedia" in query:
            topic = query.replace("wikipedia", "").strip()
            if not topic:
                return "What topic should I search on Wikipedia?"
            try:
                summary = wikipedia.summary(topic, sentences=3)
                return summary
            except:
                return "Sorry, I couldn't find that topic on Wikipedia."

        # --- OPEN APPS ---
        elif "open" in query:
            app = query.replace("open", "").strip()
            pyautogui.press("super")
            pyautogui.typewrite(app)
            pyautogui.sleep(2)
            pyautogui.press("enter")
            return f"Opening {app}"

        # --- CHAT ---
        else:
            response = ChatGpt(query)
            return response if response else "I didn’t quite get that."


# ==================== UI ====================
class AvaUI(QMainWindow):
    """Graphical Interface for Ava"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ava – AI Voice Assistant")
        self.setGeometry(400, 150, 850, 600)
        self.setStyleSheet("background:white;")

        self.core = AvaCore()

        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        # Header
        self.header = QLabel("Ava – AI Voice Assistant")
        self.header.setStyleSheet("font-size:22px; color:#007BFF; font-weight:bold; padding:10px;")

        # Date-Time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("font-size:14px; color:gray; padding:5px;")
        self.datetime_label.setAlignment(Qt.AlignRight)
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()

        # Chat Box
        self.output_box = QTextBrowser()
        self.output_box.setStyleSheet("background:#f9f9f9; color:#007BFF; font-size:15px; padding:8px; border-radius:6px;")

        # Input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your message or command here...")
        self.text_input.setStyleSheet("background:#eef5ff; color:black; font-size:14px; border-radius:5px; padding:6px;")

        # Buttons
        def make_button(label, callback):
            btn = QPushButton(label)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    background-color:#007BFF; color:white; font-weight:bold;
                    padding:8px; border:none; border-radius:8px;
                }
                QPushButton:hover { background-color:#0056b3; }
            """)
            return btn

        self.btn_send = make_button("Send", self.send_text)
        self.btn_speak = make_button("🎤 Speak", self.voice_mode)
        self.btn_img = make_button("🖼️ Image", self.ask_image_prompt)
        self.btn_ppt = make_button("📄 PowerPoint", self.ask_ppt_topic)
        self.btn_task_add = make_button("🧾 Add Task", self.add_task)
        self.btn_task_show = make_button("📋 Show Tasks", lambda: self.handle_and_show("show work"))
        self.btn_task_del = make_button("❌ Delete Task", self.delete_task)
        self.btn_ocr = make_button("🔠 OCR", lambda: self.handle_and_show("click"))
        self.btn_detect = make_button("📸 Detect", lambda: self.handle_and_show("detect"))
        self.btn_exit = make_button("🚪 Exit", lambda: sys.exit())

        for b in [self.btn_send, self.btn_speak, self.btn_img, self.btn_ppt,
                  self.btn_task_add, self.btn_task_show, self.btn_task_del,
                  self.btn_ocr, self.btn_detect, self.btn_exit]:
            btn_layout.addWidget(b)

        # Layout
        layout.addWidget(self.header)
        layout.addWidget(self.datetime_label)
        layout.addWidget(self.output_box)
        layout.addWidget(self.text_input)
        layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Greeting
        greet = "Hello, welcome to your personal assistant Ava. How may I help you today?"
        self.show_response(greet)

    # === Functions ===
    def update_time(self):
        now = datetime.datetime.now().strftime("%A, %d %B %Y | %I:%M %p")
        self.datetime_label.setText(now)

    def show_response(self, text):
        if text:
            self.output_box.append(f"<b>Ava:</b> {text}")
            self.output_box.verticalScrollBar().setValue(self.output_box.verticalScrollBar().maximum())
            print("Ava:", text)
            off(text)

    def handle_and_show(self, query):
        resp = self.core.handle_query(query)
        if resp:
            self.show_response(resp)

    def send_text(self):
        user_text = self.text_input.toPlainText().strip()
        if user_text:
            self.output_box.append(f"<b>You:</b> {user_text}")
            resp = self.core.handle_query(user_text)
            if resp:
                self.show_response(resp)
            self.text_input.clear()

    def voice_mode(self):
        off("Listening for your command...")
        q = Listen()
        if q:
            self.output_box.append(f"<b>You:</b> {q}")
            resp = self.core.handle_query(q)
            if resp:
                self.show_response(resp)

    def ask_image_prompt(self):
        self.show_response("What image should I generate?")
        prompt = self.text_input.toPlainText().strip()
        if prompt:
            self.handle_and_show(f"generate image {prompt}")

    def ask_ppt_topic(self):
        self.show_response("What topic should I make the PowerPoint on?")
        topic = self.text_input.toPlainText().strip()
        if topic:
            self.handle_and_show(f"create powerpoint {topic}")

    def add_task(self):
        task = self.text_input.toPlainText().strip()
        if not task:
            self.show_response("Please enter a task in the box first.")
            return
        self.handle_and_show(f"new task {task}")
        self.text_input.clear()

    def delete_task(self):
        task = self.text_input.toPlainText().strip()
        if not task:
            self.show_response("Please enter a task name to delete.")
            return
        self.handle_and_show(f"delete task {task}")
        self.text_input.clear()


# ==================== RUN ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvaUI()
    window.show()
    sys.exit(app.exec_())
