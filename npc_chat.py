import json
import os
from datetime import datetime
from collections import defaultdict, deque
from groq import Groq
from dotenv import load_dotenv


# ------- CONFIG -------
load_dotenv()  
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
assert GROQ_API_KEY, "You must set GROQ_API_KEY in your .env file"


client = Groq(api_key=GROQ_API_KEY)


MODEL = "llama-3.1-8b-instant"


# ----------------------


def classify_player_mood(history, latest_text, default="neutral"):
    context = "\n".join([f"Player: {msg}" for msg in history])
    prompt = f"""
You are analyzing the mood of a player talking to an NPC in a fantasy RPG.
Classify the player’s overall **tone towards the NPC** considering their last few messages.

Categories:
- friendly (asking for help, guidance, quest, directions, polite/positive requests)
- angry (insulting, rude, hostile, aggressive tone)
- neutral (anything else, casual conversation, descriptive)

Conversation history:
{context}

Latest message:
Player: "{latest_text}"

Answer in the following JSON format only:
{{
  "mood": "friendly" | "angry" | "neutral",
  "intensity": "mild" | "moderate" | "strong",
  "reason": "<brief phrase describing why>"
}}
"""
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_completion_tokens=50
        )
        result_text = completion.choices[0].message.content.strip()
        result_json = json.loads(result_text)
        mood = result_json.get("mood", default)
        intensity = result_json.get("intensity", "moderate")
        reason = result_json.get("reason", "No reason provided")
    except Exception:
        mood, intensity, reason = default, "moderate", "Parsing error or API failure"

    return mood, intensity, reason


def generate_npc_reply(player_id, message, history, mood):
    MOOD_STYLES = {
        "friendly": "Speak warmly, with encouragement. Offer helpful tips.",
        "angry": "Be curt and hostile. You may refuse to help or insult lightly.",
        "neutral": "Keep replies factual and minimal, without much emotion."
    }
    
    style = MOOD_STYLES.get(mood, "")

    context = "\n".join([f"Player: {msg}" for msg in history])

    prompt = f"""
You are an NPC in a fantasy RPG. 
The NPC mood is "{mood}". {style}

Keep responses short, immersive, and in character.

Conversation history:
{context}

Latest message:
Player: {message}
NPC:
"""
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=150
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        reply = f"(Fallback) NPC could not reply. Error: {e}"

    return reply


def main():
    # Load input JSON
    with open("players.json", "r") as f:
        messages = json.load(f)

    # Sort by timestamp
    messages.sort(key=lambda x: datetime.fromisoformat(x["timestamp"]))

    # Per-player state
    state = defaultdict(lambda: {"history": deque(maxlen=3), "mood": "neutral"})

    logs = []

    for msg in messages:
        pid = msg["player_id"]
        text = msg["text"]
        ts = msg["timestamp"]

        prev_history = list(state[pid]["history"])
        prev_mood = state[pid]["mood"]

        # classify mood using history + current message (returns mood, intensity, reason)
        mood, intensity, reason = classify_player_mood(prev_history, text, prev_mood)
        state[pid]["mood"] = mood        

        # update history
        state[pid]["history"].append(text)

        # generate reply
        npc_reply = generate_npc_reply(pid, text, list(state[pid]["history"]), mood)

        log_entry = {
            "player_id": pid,
            "message": text,
            "npc_reply": npc_reply,
            "history_used": list(state[pid]["history"]),
            "npc_mood": mood,
            "mood_intensity": intensity,
            "mood_reason": reason,
            "previous_mood": prev_mood,
            "timestamp": ts
        }
        logs.append(log_entry)

        # Pretty print
        print(f"[player_id={pid} | mood={mood} | intensity={intensity} | time={ts}]")
        print(f"Player: {text}\nNPC: {npc_reply}\n"
              f"Context: {list(state[pid]['history'])}\n---")

    # Save logs to file
    with open("npc_log.txt", "w") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
