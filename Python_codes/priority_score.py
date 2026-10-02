import pandas as pd
import re

df = pd.read_csv(r"G:\Mini_project\Dataset\grievanceiq_15k_clean.csv")

HIGH_URGENCY = [
    "fraud", "fraudulent", "unauthorized transaction", "identity theft",
    "stolen", "lawsuit", "legal action", "attorney", "sue", "scam",
    "threatened", "harassment", "discrimination", "police report",
    "illegal", "emergency"
]

MEDIUM_URGENCY = [
    "dispute", "disputed", "incorrect information", "overcharged",
    "denied", "rejected", "late fee", "credit score dropped",
    "frustrated", "delay in resolution"
]

def score_priority(text):
    if pd.isna(text):
        return "Low", []
    text = str(text).lower()

    matched_high = [kw for kw in HIGH_URGENCY if re.search(r'\b' + re.escape(kw) + r'\b', text)]
    matched_medium = [kw for kw in MEDIUM_URGENCY if re.search(r'\b' + re.escape(kw) + r'\b', text)]

    if matched_high:
        return "High", matched_high
    elif matched_medium:
        return "Medium", matched_medium
    else:
        return "Low", []

results = df["narrative_clean"].apply(score_priority)
df["priority"] = results.apply(lambda x: x[0])
df["matched_keywords"] = results.apply(lambda x: ", ".join(x[1]))

print(df["priority"].value_counts())
print()
print("Example High priority match:")
high_example = df[df["priority"] == "High"].iloc[0]
print(high_example["narrative_clean"][:200])
print("Matched:", high_example["matched_keywords"])

df.to_csv(r"G:\Mini_project\Dataset\grievanceiq_15k_priority.csv", index=False)
print()
print("Saved with priority column")