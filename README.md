# 🧙 AI-Powered NPC Chat System

This project implements a **simple AI-powered NPC (Non-Playing Character) chat system** for a fantasy RPG setting.  
Players send chat messages, and the NPC responds with short, immersive replies while maintaining **conversation history** and an evolving **mood** (`neutral`, `friendly`, `angry`).  

---

## ✨ Features
- Processes around **100 player messages** from `players.json`.
- Ensures messages are handled in **chronological order** (timestamps).
- Maintains **per-player state**:
  - Stores the **last 3 messages** for context.
  - Tracks NPC **mood** dynamically, using **LLM-based classification**.
- NPC mood classification considers the **last few messages (history + latest)**, instead of simple keyword lists.
- Immersive NPC replies are generated using **LLaMA 3.1 8B Instant**.
- Logs all interactions into **`npc_log.txt`** with:
  - `player_id`
  - `message`
  - `npc_reply`
  - `history_used`
  - `npc_mood`
  - `mood_intensity`
  - `mood_reason`
  - `previous_mood`
  - `timestamp`

*(Note: `mood_intensity` & `mood_reason` are introduced to add additional flavour or improvements beyond the basics as mentioned in the Strectch Opportunities section of assignment. `mood_change` was initially implemented for debugging but later removed for clean, minimal logs.)*

---

## 🛠️ Tech Stack
- **Language:** Python 3.10+
- **Model:** `llama-3.1-8b-instant` (via Perplexity API)
- **Environment Management:** `.env` file 
- **Dependencies:** Listed in `requirements.txt`


---

## 📤 Deliverables
- `npc_chat.py` → Main implementation
- `npc_log.txt` → Log output from a run
- `players.json` → Input dataset
- `requirements.txt` → Python dependencies
- `README.md` → Documentation
- `ai_prompts.txt`  Conversation logs with Perplexity Pro (submitted as per assignment)

---

## 🚀 Stretch Improvements
- **Mood detection** leverages **conversation history + LLM classification**, no fixed keyword lists.
- **Mood intensity** and **Mood Reason** introduced in log file to add additional flavour

---

## 🤝 Acknowledgments
- Assignment guidelines provided by course instructions.
- AI assistance: Perplexity Chat (link shared separately as part of deliverables).
