import disclosure_snippets
import re

def extract_signals(snippet: str) -> dict:
    risk_flags = []
    hedging_detected = False
    sentiment = "neutral"

    # Convert snippet to lowercase for case-insensitive matching
    snippet_lower = snippet.lower()

    # Risk Flags
    if "litigation" in snippet_lower:
        risk_flags.append("litigation")
    if "regulatory" in snippet_lower:
        risk_flags.append("regulatory")
    if re.search(r"customer concentration|top\s+\w+\s+customers", snippet_lower):
        risk_flags.append("customer concentration")

    # Hedging Detected
    if "assuming" in snippet_lower or "cautiously" in snippet_lower or "visibility" in snippet_lower:
        hedging_detected = True

    # Sentiment Classification
    if "confident" in snippet_lower or "approved" in snippet_lower:
        sentiment = "confident"
    elif hedging_detected:
        sentiment = "cautious"

    return {"risk_flags": risk_flags, "hedging_detected": hedging_detected, "sentiment": sentiment}

for full_snippet_string in disclosure_snippets.DISCLOSURE_SNIPPETS:
  # Assuming the format is 'snippet_id: snippet_text'
  parts = full_snippet_string.split(':', 1)
  snippet_id = parts[0].strip()
  snippet_text = parts[1].strip()
  signals = extract_signals(snippet_text)
  print(f"{snippet_id}: {signals}")