# =========================================================
# EXP-12: Advanced Rule-Based Chatbot (AAIT Helpdesk Bot)
# =========================================================

import random
import re
import difflib
import csv
from datetime import datetime

BOT_NAME = "AAIT Helpdesk Bot"
EXIT_COMMANDS = {"exit", "quit", "bye", "stop"}

# ---------------------------------------------------------
# Optional FAQ Loader (Create faq.csv if needed)
# ---------------------------------------------------------

FAQ_DATA = {}

def load_faq():
    try:
        with open("faq.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                FAQ_DATA[row["question"].lower()] = row["response"]
    except FileNotFoundError:
        pass  # If no CSV file, continue normally

load_faq()

# ---------------------------------------------------------
# Intent Knowledge Base
# ---------------------------------------------------------

INTENTS = {

    "greeting": {
        "patterns": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
        "responses": [
            "Hello! I am the AAIT Helpdesk Bot. How can I help you?",
            "Hi! Ask me about AAIT tools, lab experiments, or submissions."
        ]
    },

    "aait_course": {
        "patterns": ["what is aait", "aait", "application of ai tools", "ai tools course"],
        "responses": [
            "AAIT stands for Application of AI Tools. You learn tools like Trello, Figma, Visual Paradigm, Colab, Teachable Machine, and Tableau.",
            "AAIT is a hands-on lab course focused on AI tool usage and practical implementation."
        ]
    },

    "tools_info": {
        "patterns": [
            "trello", "figma", "visual paradigm", "vp",
            "teachable machine", "colab", "tableau", "github"
        ],
        "responses": [
            "AAIT tools include Trello (planning), Figma (UI design), VP (flowcharts), Colab (ML coding), Teachable Machine (model building), Tableau (visualization).",
            "Tell me the tool name and I can explain its use in AAIT."
        ]
    },

    "lab_info": {
        "patterns": [
            "lab", "experiment", "practical", "record",
            "sir lab eppudu", "lab timings cheppandi", "lab eppudu"
        ],
        "responses": [
            "In AAIT lab, focus on understanding the task and generating your own output.",
            "Keep your outputs ready and be prepared for viva."
        ]
    },

    "submission": {
        "patterns": [
            "submit", "submission", "deadline", "google form",
            "pdf", "upload", "ela submit cheyali", "submission eppudu"
        ],
        "responses": [
            "Submission is usually through Google Form or link upload.",
            "Before submitting, re-run your notebook/script fully."
        ]
    },

    "evaluation": {
        "patterns": ["marks", "evaluation", "viva", "grading", "exam"],
        "responses": [
            "Evaluation checks workflow, outputs, explanation, and reflection.",
            "Be ready to explain your steps clearly during viva."
        ]
    },

    "attendance": {
        "patterns": ["attendance", "minimum attendance", "absent rules"],
        "responses": [
            "Minimum attendance is generally 75%. Confirm with your faculty.",
            "Maintain good attendance to avoid eligibility issues."
        ]
    },

    "lab_location": {
        "patterns": ["lab location", "where is lab", "lab room", "lab number"],
        "responses": [
            "Check your timetable or department notice board for lab room details.",
            "Lab location may vary by section. Confirm with faculty."
        ]
    },

    "experiment_list": {
        "patterns": ["experiment list", "how many experiments", "exp list"],
        "responses": [
            "Refer to your syllabus or lab manual for the experiment list.",
            "AAIT includes multiple experiments covering AI tools."
        ]
    },

    "time_now": {
        "patterns": ["time now", "current time", "what time"],
        "responses": ["DYNAMIC_TIME"]
    },

    "thanks": {
        "patterns": ["thank you", "thanks", "thx"],
        "responses": ["You're welcome!", "Glad to help."]
    },

    "goodbye": {
        "patterns": ["bye", "goodbye", "see you"],
        "responses": ["Goodbye! All the best for AAIT lab."]
    }
}

UNKNOWN_RESPONSES = [
    "Sorry, I didn’t understand that. Ask about AAIT tools, lab, submission, or attendance.",
    "I’m not sure about that. Please ask something related to AAIT lab."
]

# ---------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------

def preprocess(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------------------------------------------
# Intent Matching with Fuzzy Logic
# ---------------------------------------------------------

def match_intent(user_text: str) -> str:
    text = preprocess(user_text)
    tokens = set(text.split())

    best_intent = None
    best_score = 0

    for intent, data in INTENTS.items():
        score = 0

        for pat in data["patterns"]:
            pat_clean = preprocess(pat)

            # Phrase match
            if " " in pat_clean:
                if pat_clean in text:
                    score += 2
            else:
                # Fuzzy matching for single words
                for token in tokens:
                    similarity = difflib.SequenceMatcher(None, pat_clean, token).ratio()
                    if similarity > 0.8:
                        score += 1

        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent if best_score > 0 else "unknown"

# ---------------------------------------------------------
# Generate Response (With Memory)
# ---------------------------------------------------------

def get_response(user_text: str, context: dict) -> str:
    cleaned = preprocess(user_text)

    # Check FAQ first
    if cleaned in FAQ_DATA:
        return FAQ_DATA[cleaned]

    intent = match_intent(user_text)

    # Follow-up memory for tools
    if intent == "unknown" and context["last_intent"] == "tools_info":
        for tool in ["trello", "figma", "colab", "visual paradigm", "vp", "tableau"]:
            if tool in cleaned:
                return f"{tool.title()} is used in AAIT for practical implementation tasks."

    context["last_intent"] = intent

    if intent == "time_now":
        now = datetime.now().strftime("%I:%M %p")
        return f"Current time is {now}."

    if intent == "unknown":
        return random.choice(UNKNOWN_RESPONSES)

    return random.choice(INTENTS[intent]["responses"])

# ---------------------------------------------------------
# Chat Loop
# ---------------------------------------------------------

def chat():
    print(f"{BOT_NAME}: Hi! Type 'exit' to quit.")
    context = {"last_intent": None}

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print(f"{BOT_NAME}: Please type something.")
            continue

        if preprocess(user_input) in EXIT_COMMANDS:
            print(f"{BOT_NAME}: Goodbye!")
            break

        reply = get_response(user_input, context)
        print(f"{BOT_NAME}: {reply}")

# ---------------------------------------------------------
# Run Bot
# ---------------------------------------------------------

if __name__ == "__main__":
    chat()
