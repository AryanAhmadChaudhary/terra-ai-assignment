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


def classify_mood_with_groq(history, latest_text, default="neutral"):
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

Answer with only one word: "friendly", "angry", or "neutral".
"""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0, 
            max_completion_tokens=10
        )
        result = completion.choices[0].message.content.strip().lower()
        if result in ["friendly", "angry", "neutral"]:
            return result
        else:
            return default
    except Exception:
        return default


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

        # classify mood using history + current message
        mood = classify_mood_with_groq(prev_history, text, prev_mood)
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
            "previous_mood": prev_mood,
            "timestamp": ts
        }
        logs.append(log_entry)

        # Pretty print
        print(f"[player_id={pid} | mood={mood} | time={ts}]")
        
        print(f"Player: {text}\nNPC: {npc_reply}\n"
              f"Context: {list(state[pid]['history'])}\n---")

    # Save logs to file
    with open("npc_log.txt", "w") as f:
        for entry in logs:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
