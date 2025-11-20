import json, os, subprocess, uuid
import pyttsx3
import datetime

CONFIG = "config.json"
MEMORY = "memory.json"
MODEL_PATH = "../models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
EXEC = "../llama/codexedge.exe"

# Initialize TTS
engine = pyttsx3.init()

# Load or create memory
if not os.path.exists(MEMORY):
    with open(MEMORY, "w") as f:
        json.dump([], f)

# Load or create config
if not os.path.exists(CONFIG):
    with open(CONFIG, "w") as f:
        json.dump({"threads": 6, "temp": 0.7}, f)

def load_memory():
    with open(MEMORY, "r") as f:
        return json.load(f)

def save_memory(log):
    with open(MEMORY, "w") as f:
        json.dump(log, f, indent=2)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def run_model(prompt, config):
    full_prompt = f"[INST] {prompt} [/INST]"
    args = [
        EXEC,
        f"file://{MODEL_PATH}",
        "--threads", str(config.get("threads", 6)),
        "--temp", str(config.get("temp", 0.7))
    ]
    process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    try:
        output, _ = process.communicate(full_prompt, timeout=90)
        return output.strip().splitlines()[-1]  # last line = response
    except subprocess.TimeoutExpired:
        return "CodexEdge timed out..."

def main():
    config = json.load(open(CONFIG))
    history = load_memory()

    print("🧠 CodexEdge CLI Assistant (offline)")
    print("Type 'exit' to quit\n")

    while True:
        user = input("You > ").strip()
        if user.lower() in ["exit", "quit"]:
            break

        print("CodexEdge is thinking...")
        response = run_model(user, config)

        print(f"CodexEdge > {response}")
        speak(response[:250])  # avoid long text

        history.append({
            "id": str(uuid.uuid4()),
            "timestamp": str(datetime.datetime.now()),
            "user": user,
            "response": response
        })
        save_memory(history)

if __name__ == "__main__":
    main()
