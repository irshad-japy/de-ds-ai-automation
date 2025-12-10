"""
python ai-youtube-automation/app/services/generate_hoos.py
"""

import re
from collections import Counter
from typing import List, Dict, Any

# Very small custom stopword list (can extend)
STOPWORDS = {
    "the", "a", "an", "and", "or", "in", "on", "at", "of", "to", "for",
    "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those",
    "with", "by", "from", "as", "it", "its",
    "you", "your", "yours", "their", "they", "them",
    "we", "our", "ours", "i", "me", "my", "mine",
    "but", "if", "so", "not", "no", "yes",
    "can", "will", "just", "really", "very",
    "video", "today", "now", "one",
}


def split_sentences(text: str) -> List[str]:
    """Naive sentence splitter based on punctuation."""
    # Normalize line breaks
    text = text.replace("\n", " ")
    # Split at . ? !
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences

def tokenize(text: str) -> List[str]:
    """Lowercase and extract simple word tokens, filtering stopwords."""
    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]+\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

def extract_summary(sentences: List[str], max_sentences: int = 3) -> List[str]:
    """
    Simple frequency-based summarizer:
    - Count word frequencies across all sentences
    - Score each sentence by sum of word frequencies
    - Return top N sentences in original order
    """
    if not sentences:
        return []

    all_text = " ".join(sentences)
    words = tokenize(all_text)
    freq = Counter(words)

    if not freq:
        # fallback: first N sentences
        return sentences[:max_sentences]

    # Score sentences
    sentence_scores = {}
    for s in sentences:
        tokens = tokenize(s)
        sentence_scores[s] = sum(freq[w] for w in tokens)

    # Rank by score (desc), keep top N
    ranked = sorted(sentences, key=lambda s: sentence_scores.get(s, 0), reverse=True)
    top_set = set(ranked[:max_sentences])

    # Preserve original order
    summary = [s for s in sentences if s in top_set]
    return summary

def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """Get top-N frequent non-stopword tokens as rough 'keywords'."""
    tokens = tokenize(text)
    common = [w for w, _ in Counter(tokens).most_common(top_n)]
    return common

def guess_main_pain(sentences: List[str]) -> str:
    """Try to find a sentence that sounds like a pain/problem."""
    pain_keywords = [
        "tired", "waste", "wasting", "boring", "manual",
        "confusing", "hard", "difficult", "problem",
        "struggle", "frustrating", "slow", "time-consuming",
        "overwhelmed",
    ]
    for s in sentences:
        lower = s.lower()
        if any(k in lower for k in pain_keywords):
            return s
    return sentences[0] if sentences else ""

def guess_main_promise(sentences: List[str]) -> str:
    """Try to find a sentence that sounds like a promise/benefit."""
    promise_keywords = [
        "you can", "you will", "you'll", "this video will",
        "help you", "show you", "teach you", "learn how to",
        "save time", "save hours", "faster", "easier",
        "step by step", "in minutes", "automate",
    ]
    for s in sentences:
        lower = s.lower()
        if any(k in lower for k in promise_keywords):
            return s
    # fallback: maybe second sentence or last
    if len(sentences) > 1:
        return sentences[1]
    return sentences[0] if sentences else ""

def guess_unique_angle(sentences: List[str]) -> str:
    """
    Try to find a sentence that hints at a unique angle:
    - mentions AI, automation, n8n, workflow, etc.
    """
    angle_keywords = [
        "automation", "automate", "ai", "n8n", "workflow",
        "agent", "youtube automation", "no code", "low code",
        "end to end", "from scratch",
    ]
    for s in sentences:
        lower = s.lower()
        if any(k in lower for k in angle_keywords):
            return s
    # fallback: summary first sentence or overall first sentence
    return sentences[0] if sentences else ""


def build_hooks(
    main_pain: str,
    main_promise: str,
    keywords: List[str],
) -> Dict[str, str]:
    """
    Create 5 hooks using templates and extracted info.
    keywords[0] will be used as main topic if available.
    """
    topic = keywords[0] if keywords else "this process"

    # Make them a bit generic and editable later
    hooks = {}

    # 1. Pain → Fast Fix
    hooks["pain_fast_fix"] = (
        f"Still dealing with {topic} the hard way? "
        f"Let me show you a faster, easier fix."
    )

    # 2. What if...
    hooks["what_if"] = (
        f"What if {topic} could run on autopilot while you focus on real work?"
    )

    # 3. Hidden mistake
    hooks["hidden_mistake"] = (
        f"Most people make one silent mistake with {topic} that wastes hours—"
        f"let's fix it now."
    )

    # 4. Mini case study / result
    hooks["mini_case_study"] = (
        f"I used this simple {topic} setup to save hours every week. "
        f"I'll walk you through it."
    )

    # 5. Challenge / pattern interrupt
    hooks["challenge"] = (
        f"Give me 10 seconds—if you still do {topic} manually after this, "
        f"that’s on you."
    )

    return hooks

def analyze_script(text: str) -> Dict[str, Any]:
    """
    Main function:
    - Split into sentences
    - Extract summary and main points
    - Guess pain, promise, unique angle
    - Extract keywords
    - Generate 5 hooks
    """
    sentences = split_sentences(text)
    summary_sentences = extract_summary(sentences, max_sentences=3)

    main_pain = guess_main_pain(sentences)
    main_promise = guess_main_promise(sentences)
    unique_angle = guess_unique_angle(sentences)

    keywords = extract_keywords(text, top_n=5)
    hooks = build_hooks(main_pain, main_promise, keywords)  

    result = {
        "summary_sentences": summary_sentences,
        "keywords": keywords,
        "main_pain": main_pain,
        "main_promise": main_promise,
        "unique_angle": unique_angle,
        "hooks": hooks,
    }
    return result

if __name__ == "__main__":
    # Simple CLI usage: python script_hook_analyzer.py path/to/script.txt
    

    script_path = 'C:/Users/ermdi/projects/ird-projects/de-ds-ai-automation/output/ROmtgqTefAw_transcript_20251210_102926.txt'
    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    analysis = analyze_script(script_text)

    print("=== SUMMARY (main points) ===")
    for s in analysis["summary_sentences"]:
        print("-", s)

    print("\n=== KEYWORDS ===")
    print(", ".join(analysis["keywords"]))

    print("\n=== MAIN PAIN ===")
    print(analysis["main_pain"])

    print("\n=== MAIN PROMISE ===")
    print(analysis["main_promise"])

    print("\n=== UNIQUE ANGLE ===")
    print(analysis["unique_angle"])

    print("\n=== HOOKS ===")
    for name, text in analysis["hooks"].items():
        print(f"[{name}] {text}")
