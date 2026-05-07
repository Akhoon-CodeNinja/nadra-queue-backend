# 🏛️ NADRA AI-Based Queue Management & Smart Assistant System

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-Backend-darkgreen)
![AI](https://img.shields.io/badge/AI-PyTorch%20%7C%20YOLOv8%20%7C%20FAISS-orange)

---

# 📌 Project Overview

This project is an intelligent **Queue Management and Virtual Assistant System** designed for **NADRA (National Database and Registration Authority)** or similar public service centers.

The system combines **Artificial Intelligence, Computer Vision, Voice Processing, and Retrieval-Augmented Generation (RAG)** to automate queue monitoring, estimate waiting times, and provide citizens with a smart voice-enabled assistant that answers queries based on official NADRA policies and documents.

---

# ✨ Key Features

## 1️⃣ AI-Powered Smart Chatbot (RAG Based)
- Uses **Retrieval-Augmented Generation (RAG)** for accurate responses.
- Retrieves answers from official NADRA documents.
- Generates intelligent responses using **Groq LLM API**.
- Supports both **Text** and **Voice Queries**.

---

## 2️⃣ Voice-to-Text Assistant
- Converts Urdu/English speech into text using **OpenAI Whisper**.
- Enables citizens to interact naturally with the system.

---

## 3️⃣ Real-Time Queue Monitoring
- Uses **YOLOv8 Object Detection** for live people counting.
- Estimates waiting time dynamically based on queue size.
- Works efficiently on CPU-only systems.

---

## 4️⃣ Cross-Platform Mobile Application
- Frontend developed using **Flutter**.
- Communicates with Django backend using REST APIs.
- Can run on:
  - Android Devices
  - BlueStacks Emulator

---

# 🏗️ System Architecture

```text
        User Voice/Text Query
                  │
                  ▼
        Flutter Mobile App
                  │
                  ▼
        Django REST API Backend
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   RAG Chatbot         YOLOv8 Vision
        │                   │
        ▼                   ▼
  FAISS Vector DB     Live Camera Feed
        │
        ▼
   Groq LLM Response
