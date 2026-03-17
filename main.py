import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import json
import os
import random
import threading
import queue
import speech_recognition as sr
import pyttsx3
import cohere

class VoiceMentalHealthCompanion:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice AI Mental Health Companion - MOODMATE🤗")
        self.root.geometry("700x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#34495E")
        # Variables
        self.user_name = None
        self.mood_history = []
        self.catching_advice = False
        self.face_emotion = "Unknown"
        self.current_question_index = 0
        self.user_answers = []
        self.in_assessment = True

        # Thread-safe queue for processing voice input asynchronously
        self.queue = queue.Queue()

        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 160)

        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Resources to suggest
        self.resources = [
            {"topic": "Anxiety Support", "link": "https://www.anxietycanada.com/articles/what-is-anxiety/"},
            {"topic": "Depression Info", "link": "https://www.nimh.nih.gov/health/topics/depression"},
            {"topic": "Mindfulness", "link": "https://www.mindful.org/meditation/mindfulness-getting-started/"},
            {"topic": "Stress Management", "link": "https://www.apa.org/topics/stress"},
            {"topic": "Suicide Prevention", "link": "https://suicidepreventionlifeline.org/"},
            {"topic": "Crisis Support", "link": "https://www.crisistextline.org/"},
        ]

        # Sentiment keyword maps for quick heuristic
        self.sentiment_map = {
            "positive": ["happy", "good", "great", "fine", "well", "awesome", "okay", "joy", "love", "calm", "excited", "relaxed", "content"],
            "negative": ["sad", "down", "depressed", "anxious", "stressed", "angry", "upset", "lonely", "tired", "worried", "hurt", "bad", "unhappy", "miserable"],
            "neutral":  ["so-so", "okay", "alright", "meh", "fine", "average", "indifferent"],
        }

        # Responses refined for better analysis feedback
        self.responses = {
            "greeting": [
                "Hello! How are you feeling today? Feel free to share anything on your mind.",
                "Hi! I'm here to listen to you. How do you feel right now?",
                "Hey there! Tell me about your day or how you've been feeling lately.",
            ],
            "positive": [
                "I'm glad to hear you're doing well. What made you feel this way?",
                "That's wonderful! Shall I share some tips to keep your positivity?",
                "You seem positive today. Keep nurturing those good feelings!",
            ],
            "negative": [
                "I'm sorry to hear that. Would you like to talk more about what's troubling you?",
                "It’s okay to feel low sometimes. I'm here to listen.",
                "Sharing your feelings might help lessen their weight. I'm here.",
            ],
            "neutral": [
                "Thanks for sharing. Feel free to tell me more.",
                "I understand. If you want, we can explore ways to boost your mood.",
                "Okay, take your time. I'm here whenever you're ready.",
            ],
            "unknown": [
                "Thanks for sharing. Can you please elaborate a little more?",
                "I’m listening. How does that make you feel?",
                "Feel free to tell me more when you want.",
            ],
            "analysis": [
                "Based on how you’ve shared, here are some suggestions that might help.",
                "Considering what you told me, I have some advice to support you.",
                "From what I understood, here are some tips that could be useful.",
            ]
        }

        # Assessment questions
        self.assessment_questions = [
            "How have you been feeling emotionally over the past week?",
            "Have you experienced any changes in your sleep patterns recently?",
            "How is your appetite and energy level these days?",
            "Have you felt anxious, worried, or stressed more than usual?",
            "Are you finding it difficult to enjoy things you used to like?",
            "Have you had any trouble concentrating or making decisions?",
            "Do you feel supported by friends or family?",
            "Is there anything in particular that's been on your mind lately?",
            "Have you had any thoughts of self-harm or feeling hopeless?",
            "What would you like to improve about your mental health?"
        ]

        # Build GUI
        self.setup_gui()

        # Load saved user data if available
        self.load_user_data()
        if not self.user_name:
            self.ask_user_name()
        else:
            self.in_assessment = True
            self.current_question_index = 0
            self.user_answers = []
            self.chat("Let's begin your mental health checkup. Please answer the following questions honestly.")
            self.chat(self.assessment_questions[0])

        # Start queue processing
        self.root.after(100, self.process_queue)

    def setup_gui(self):
        title = tk.Label(self.root, text="Voice AI Mental Health Companion - Conversation Analyzer",
                         font=("Helvetica", 13, "bold"), fg="white", bg="#34495E")
        title.pack(pady=6)

        # --- Mood History Table ---
        mood_frame = tk.Frame(self.root, bg="#34495E")
        mood_frame.pack(padx=8, pady=(0, 4), fill="x")
        mood_label = tk.Label(mood_frame, text="Mood History", font=("Calibri", 10, "bold"), fg="white", bg="#34495E")
        mood_label.pack(anchor="w")
        self.mood_table = ttk.Treeview(mood_frame, columns=("Mood", "Time"), show="headings", height=3)
        self.mood_table.heading("Mood", text="Mood")
        self.mood_table.heading("Time", text="Time")
        self.mood_table.column("Mood", width=80)
        self.mood_table.column("Time", width=140)
        self.mood_table.pack(fill="x")
        self.update_mood_table()

        # --- Chat Area ---
        chat_frame = tk.Frame(self.root, bg="#2C3E50", bd=2, relief="sunken")
        chat_frame.pack(fill="both", expand=True, padx=8, pady=(0,4))

        self.chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', font=("Calibri", 10),
                                                   bg="#2C3E50", fg="white", wrap=tk.WORD, height=15)
        self.chat_area.pack(fill="both", expand=True)

        # --- Input Area ---
        input_frame = tk.Frame(self.root, bg="#34495E")
        input_frame.pack(fill="x", padx=8, pady=(0,6))

        input_label = tk.Label(input_frame, text="Type your message here:", font=("Calibri", 9), fg="white", bg="#34495E")
        input_label.pack(anchor="w", side="top", pady=(0,2))

        self.user_input = tk.Entry(input_frame, font=("Calibri", 11))
        self.user_input.pack(side="left", fill="x", expand=True, ipady=4, pady=2)
        self.user_input.bind("<Return>", self.on_send)

        send_button = tk.Button(input_frame, text="Send (Text)", font=("Calibri", 9, "bold"),
                                bg="#2980B9", fg="white", command=self.on_send)
        send_button.pack(side="right", padx=(4,0), pady=2, ipadx=5)

        voice_button = tk.Button(input_frame, text="Speak (Voice)", font=("Calibri", 9, "bold"),
                                 bg="#27AE60", fg="white", command=self.start_listening)
        voice_button.pack(side="right", padx=(4,0), pady=2, ipadx=5)

        reset_button = tk.Button(input_frame, text="Reset Data", font=("Calibri", 9, "bold"),
                                 bg="#E74C3C", fg="white", command=self.reset_data)
        reset_button.pack(side="right", padx=(4,0), pady=2, ipadx=5)

        self.use_ollama = tk.BooleanVar()
        ollama_checkbox = tk.Checkbutton(
            input_frame, text="Analyze with Ollama (local AI)", variable=self.use_ollama,
            bg="#34495E", fg="white", selectcolor="#34495E", font=("Calibri", 9)
        )
        ollama_checkbox.pack(side="right", padx=(4,0))

        self.emotion_label = tk.Label(self.root, text="Detected Face Emotion: Unknown",
                                      font=("Calibri", 8), fg="white", bg="#34495E")
        self.emotion_label.pack(pady=(0,4))

        # --- Resources Table ---
        resources_frame = tk.Frame(self.root, bg="#34495E")
        resources_frame.pack(padx=8, pady=(0,4), fill="x")
        resources_label = tk.Label(resources_frame, text="Helpful Resources", font=("Calibri", 10, "bold"), fg="white", bg="#34495E")
        resources_label.pack(anchor="w")
        self.resources_table = ttk.Treeview(resources_frame, columns=("Topic", "Link"), show="headings", height=3)
        self.resources_table.heading("Topic", text="Topic")
        self.resources_table.heading("Link", text="Link")
        self.resources_table.column("Topic", width=120)
        self.resources_table.column("Link", width=350)
        self.resources_table.pack(fill="x")
        self.populate_resources_table()
        self.resources_table.bind("<Double-1>", self.open_resource_link)

    def update_mood_table(self):
        for row in self.mood_table.get_children():
            self.mood_table.delete(row)
        import datetime
        for mood, timestamp in self.mood_history[-10:]:
            self.mood_table.insert("", "end", values=(mood, timestamp))

    def populate_resources_table(self):
        for row in self.resources_table.get_children():
            self.resources_table.delete(row)
        for res in self.resources:
            self.resources_table.insert("", "end", values=(res["topic"], res["link"]))

    def open_resource_link(self, event):
        import webbrowser
        item = self.resources_table.selection()
        if item:
            link = self.resources_table.item(item, "values")[1]
            webbrowser.open(link)

    def reset_data(self):
        if messagebox.askyesno("Reset Data", "Are you sure you want to clear your mood history?"):
            self.mood_history = []
            self.save_user_data()
            self.update_mood_table()
            self.chat_area.config(state='normal')
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state='disabled')
            self.chat("Mood history has been reset.")

    def ask_user_name(self):
        def submit_name():
            name = input_name.get().strip()
            if not name:
                messagebox.showwarning("Name Missing", "Please enter your name to continue.")
                return
            self.user_name = name
            self.save_user_data()
            top.destroy()
            self.chat(f"Hello {self.user_name}! {random.choice(self.responses['greeting'])}")

        top = tk.Toplevel(self.root)
        top.title("Welcome!")
        top.geometry("350x150")
        top.config(bg="#34495E")
        top.resizable(False, False)

        label = tk.Label(top, text="Please enter your name:", font=("Calibri", 12),
                         fg="white", bg="#34495E")
        label.pack(pady=(20,5))

        input_name = tk.Entry(top, font=("Calibri", 14))
        input_name.pack(pady=5, padx=15, fill="x")
        input_name.focus()

        submit_btn = tk.Button(top, text="Submit", font=("Calibri", 12, "bold"),
                               bg="#2980B9", fg="white", command=submit_name)
        submit_btn.pack(pady=10)

        top.grab_set()
        self.root.wait_window(top)

    def chat(self, text, user=False):
        self.chat_area.config(state='normal')
        if user:
            self.chat_area.insert(tk.END, f"{self.user_name}: {text}\n\n")
        else:
            self.chat_area.insert(tk.END, f"AI Companion: {text}\n\n")
            threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def _speak_thread(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def on_send(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        self.user_input.delete(0, tk.END)
        self.chat(user_text, user=True)

        if self.in_assessment:
            self.user_answers.append(user_text)
            self.current_question_index += 1
            if self.current_question_index < len(self.assessment_questions):
                self.chat(self.assessment_questions[self.current_question_index])
            else:
                self.in_assessment = False
                summary = self.summarize_assessment()
                self.chat("Thank you for your responses. Processing your assessment...")
                self.root.after(1500, lambda: self.get_cohere_analysis(summary))
        else:
            self.analyze_and_respond(user_text)

    def summarize_assessment(self):
        summary = "Here is the user's mental health self-assessment:\n"
        for q, a in zip(self.assessment_questions, self.user_answers):
            summary += f"Q: {q}\nA: {a}\n"
        return summary

    def get_cohere_analysis(self, summary):
        analysis = self.analyze_with_cohere(summary)
        self.chat("Cohere AI Analysis:\n" + analysis)

    def start_listening(self):
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _listen_thread(self):
        self.chat("Listening... Please speak now.", user=False)
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=7)
                user_text = self.recognizer.recognize_google(audio)
                self.queue.put(user_text)
            except sr.WaitTimeoutError:
                self.queue.put("[Voice Input Timeout]")
            except sr.UnknownValueError:
                self.queue.put("[Could not understand audio]")
            except sr.RequestError:
                self.queue.put("[Error with speech recognition service]")
            except Exception as e:
                self.queue.put(f"[Error: {e}]")

    def process_queue(self):
        try:
            while True:
                user_text = self.queue.get_nowait()
                if user_text.startswith("["):
                    self.chat(user_text)
                else:
                    self.chat(user_text, user=True)
                    self.analyze_and_respond(user_text)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

    def analyze_and_respond(self, user_text):
        if getattr(self, "use_ollama", None) and self.use_ollama.get():
            self.chat("Analyzing your message with Ollama...", user=False)
            analysis = self.analyze_with_ollama(user_text)
            self.chat("Ollama AI Analysis:\n" + analysis, user=False)
        else:
            self.chat("Analyzing your message with Cohere...", user=False)
            analysis = self.analyze_with_cohere(user_text)
            self.chat("Cohere AI Analysis:\n" + analysis, user=False)

        sentiment = self.detect_sentiment(user_text)
        face_emotion = getattr(self, "face_emotion", "Unknown").lower()

        if sentiment == "negative" or "sad" in face_emotion or "serious" in face_emotion:
            response_category = "negative"
        elif sentiment == "positive" and ("happy" in face_emotion or "smile" in face_emotion):
            response_category = "positive"
        elif sentiment == "neutral":
            response_category = "neutral"
        else:
            response_category = "unknown"

        response_text = random.choice(self.responses.get(response_category, self.responses["unknown"]))
        self.chat(response_text, user=False)

        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.mood_history.append((response_category, now))
        self.save_user_data()
        self.update_mood_table()

        if len(self.mood_history) >= 4 and not self.catching_advice:
            self.catching_advice = True
            advice_text = self.provide_advice()
            self.chat(advice_text, user=False)

    def detect_sentiment(self, text):
        text = text.lower()
        for feeling, keywords in self.sentiment_map.items():
            for kw in keywords:
                if kw in text:
                    return feeling
        return "unknown"

    def provide_advice(self):
        neg = sum(1 for mood, _ in self.mood_history if mood == "negative")
        pos = sum(1 for mood, _ in self.mood_history if mood == "positive")
        if neg > pos:
            return ("It seems you might be struggling lately. "
                    "Consider speaking to someone you trust or a mental health professional. "
                    "Check the resources above for help.")
        elif pos > neg:
            return ("Glad you're feeling positive! Keep engaging in activities that support your wellbeing.")
        else:
            return ("Your feelings seem mixed. Taking care of yourself and connecting with loved ones can help.")

    def analyze_with_cohere(self, user_text):
        api_key = "q9TloGEOENHlKAzlwlm03mnS6CwD8CXYGd4kZ5Sy"  # <-- Replace with your Cohere API key
        co = cohere.Client(api_key)
        try:
            response = co.chat(
                model="command-r-plus",  # Or "command", "command-light", etc.
                message=user_text,
                chat_history=[],
                temperature=0.7,
                max_tokens=500
            )
            return response.text.strip()
        except Exception as e:
            return f"Sorry, Cohere error: {e}"

    def save_user_data(self):
        data = {
            "user_name": self.user_name,
            "mood_history": self.mood_history
        }
        try:
            with open("voice_mental_health_data.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving user data: {e}")

    def load_user_data(self):
        if os.path.exists("voice_mental_health_data.json"):
            try:
                with open("voice_mental_health_data.json", "r") as f:
                    data = json.load(f)
                    self.user_name = data.get("user_name")
                    self.mood_history = data.get("mood_history", [])
            except Exception:
                self.user_name = None
                self.mood_history = []
        else:
            self.user_name = None
            self.mood_history = []

    def on_closing(self):
        self.root.destroy()

    def start_webcam(self):
        pass

    def analyze_with_ollama(self, user_text):
        try:
            url = "http://localhost:11434/api/generate"
            data = {
                "model": "llama3",
                "prompt": f"You are a helpful mental health assistant. User says: {user_text}",
                "stream": False
            }
            import requests
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return "Sorry, I couldn't analyze your message with Ollama."
        except Exception as e:
            return f"Ollama error: {e}"

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceMentalHealthCompanion(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
