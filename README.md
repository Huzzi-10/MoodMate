# MoodMate(Monitoring & Optimizing Overall Dynamic Mental Awareness Through Engagement)
AI-powered multimodal mental health companion that analyzes user emotions through voice and text to provide personalized support, assessment, and well-being guidance.

<br>
## **Overview**

MoodMate is designed to provide a **safe, supportive, and interactive environment** for users to share their emotions and track their mental well-being. It combines **text and voice interactions**, sentiment analysis, and AI-powered feedback to create a **personalized mental health companion experience**.

- Conducts **self-assessment** through a set of predefined mental health questions.
- Tracks **user mood over time** and displays it in an interactive GUI.
- Offers **AI-generated insights** using Cohere AI (cloud) and Ollama (local AI model).
- Provides **advice and resources** for improving mental health.

---

## **Key Features**

- **Text & Voice Interaction**: Users can type messages or speak directly to MoodMate.  
- **Real-Time Sentiment Analysis**: Quick mood detection (positive, negative, neutral, unknown) based on text input and keywords.  
- **Mental Health Assessment**: 10-question questionnaire to evaluate emotional well-being.  
- **AI-Based Insights**: Integration with **Cohere AI** and **Ollama AI** for advanced message analysis and personalized responses.  
- **Mood History Tracking**: Displays a table of mood trends over time with timestamps.  
- **Resource Recommendations**: Provides helpful links for mental health support.  
- **Personalized Advice**: Suggests guidance based on overall mood trends.  
- **Persistent User Data**: Stores user name and mood history locally in a JSON file.  
- **GUI-Based User Experience**: Built using Tkinter with interactive chat area, tables, and buttons.  
- **Multithreading for Smooth Interaction**: Voice input and AI processing handled asynchronously to prevent GUI freezing.

---

## **How It Works**

1. **User Registration**: The system prompts the user for their name on first use.  
2. **Mental Health Assessment**: Users answer a series of 10 predefined questions about their emotional state, sleep, energy, anxiety, and social support.  
3. **Analysis**: AI models analyze the responses and provide insights.  
4. **Chat Mode**: Users can continue interacting via text or voice; MoodMate responds with context-aware and AI-enhanced feedback.  
5. **Mood Tracking**: Each interaction updates the user's mood history and stores it locally.  
6. **Advice & Resources**: Based on mood patterns, personalized advice and external resource links are offered.

---

## **Technologies Used**

- **Python 3.x**
- **Tkinter** – GUI interface
- **SpeechRecognition** – Voice input capture
- **PyTTSX3** – Text-to-speech engine
- **Cohere API** – Cloud AI for NLP analysis
- **Ollama API** – Local AI model integration
- **JSON** – User data storage
- **Threading & Queue** – Asynchronous processing for smooth GUI
- **Requests** – API communication

