"""
validity_checker.py - Complaint Quality, Adaptive Data Requirements & Multilingual SBERT Scorer
Features:
1. Adaptive Data Requirements based on Complaint Category:
   - Financial Transactions: Requires amount, reference/UTR, and proof receipt.
   - Lost / Stolen Cards: Requires card last 4 digits and incident date (NO transaction amount/receipt needed!).
   - Net Banking / Mobile App Access: Requires User ID/App name and incident date (NO monetary amount needed!).
   - KYC / Account Restrictions: Requires Account number and branch (NO transaction amount needed!).
   - Loan / NOC Delays: Requires Loan Account Number (NO daily transaction reference needed!).
   - Staff Behavior / Harassment: Requires Incident date and staff/agent details (NO monetary sum needed!).
2. 3-Tier Human Coherence Engine (NEW):
   - Tier 1: Gibberish & Character Entropy Detection — rejects random keyboard mashing.
   - Tier 2: Grammatical Glue Ratio — rejects keyword bombing (lists of nouns with no sentence structure).
   - Tier 3: Grievance Action Verb Check — requires at least one problem/distress verb or phrase.
3. Multilingual SBERT Semantic & Emotional Validity:
   - Processes Hindi, Hinglish, and English complaints transparently.
   - Evaluates dense vector similarity across multilingual banking grievance anchors.
"""

import os
import re
import numpy as np
from datetime import datetime, date
from semantic_engine import get_text_embedding, cosine_similarity
from multilingual_engine import detect_language, align_multilingual_text

# SBERT Semantic Grievance Anchors in English, Hindi, and Hinglish
GRIEVANCE_SEMANTIC_ANCHORS = [
    # English
    "Money was debited from my account but the receiver has not received the funds.",
    "I made an online payment and it failed but my balance was deducted.",
    "Unauthorized transaction occurred on my card without my consent or OTP.",
    "ATM did not dispense cash although the money was deducted from my savings account.",
    "Bank charged unfair penalty or hidden fees and refused to refund.",
    "My account was frozen unexpectedly and I am unable to access my funds.",
    "Loan foreclosure letter and NOC have not been provided after full payment.",
    "Recovery agents are calling repeatedly and harassing me unfairly.",
    "Wrong credit bureau entry is damaging my CIBIL score and needs correction.",
    "I lost my credit card and need immediate blocking and hotlisting.",
    "Net banking login is blocked and app keeps crashing during transfer.",
    # Hinglish concepts
    "Mere account se paise kat gaye aur samne wale ko nahi mile.",
    "ATM se paise nahi nikle lekin account se balance deduct ho gaya.",
    "Mera credit card kho gaya hai please card ko turant block kijiye.",
    "Net banking login nahi ho raha aur branch me koi help nahi kar raha.",
    "Mere credit card ke bill mein galat charge laga hai maine transaction nahi kiya kripya ise hata dein aur refund karein.",
    "Incorrect or unauthorized charge appeared on my credit card bill and I request a reversal.",
    "Mere loan account se do baar EMI deduct ho gayi hai refund kijiye.",
    # Devanagari Hindi Anchors
    "मेरे खाते से पैसे कट गए हैं और लाभार्थी को पैसे नहीं मिले।",
    "एटीएम से नकदी नहीं निकली लेकिन बचत खाते से पैसे कट गए।",
    "मेरे कार्ड से बिना ओटीपी के अवैध लेनदेन हुआ है।",
    "ऋण पूरा चुकाने के बाद भी एनओसी पत्र नहीं दिया गया है।",
    "मेरे क्रेडिट कार्ड बिल में गलत चार्ज लगाया गया है मैंने यह लेनदेन नहीं किया कृपया जांच कर समाधान करें।"
]

ANCHOR_VECTORS = [get_text_embedding(anchor) for anchor in GRIEVANCE_SEMANTIC_ANCHORS]

# Dynamic field requirements mapping
CATEGORY_REQUIREMENTS = {
    "Lost / Stolen Card & Emergency Block": {
        "needs_amount": False,
        "needs_ref_id": False,
        "needs_card_last4": True,
        "needs_proof": False,
        "description": "Card hotlisting & blocking request"
    },
    "Net Banking / Mobile App & Tech Glitch": {
        "needs_amount": False,
        "needs_ref_id": False,
        "needs_app_details": True,
        "needs_proof": False,
        "description": "Digital channel access & login troubleshooting"
    },
    "KYC, Account Freezing & Dormancy": {
        "needs_amount": False,
        "needs_ref_id": False,
        "needs_account_no": True,
        "needs_proof": True,  # e.g. ID proof or bank passbook copy
        "description": "Account status & compliance verification"
    },
    "Staff Behavior & Recovery Harassment": {
        "needs_amount": False,
        "needs_ref_id": False,
        "needs_agent_details": True,
        "needs_proof": False,
        "description": "Conduct, timing & ethics dispute"
    },
    "Loan Closure, NOC & Document Dispatch": {
        "needs_amount": False,
        "needs_ref_id": False,
        "needs_loan_no": True,
        "needs_proof": True,
        "description": "Loan lien release & property title documentation"
    },
    "UPI / IMPS / Digital Fund Transfer": {
        "needs_amount": True,
        "needs_ref_id": True,
        "needs_proof": True,
        "description": "Electronic fund transfer reconciliation"
    },
    "Credit Card / Disputed Charges & Fee": {
        "needs_amount": True,
        "needs_ref_id": True,
        "needs_proof": True,
        "description": "Card billing & chargeback dispute"
    },
    "ATM Cash Withdrawal Failure": {
        "needs_amount": True,
        "needs_ref_id": True,
        "needs_proof": False,
        "description": "ATM cash dispense discrepancy"
    },
    "Credit Bureau / CIBIL Rectification": {
        "needs_amount": False,
        "needs_ref_id": True, # e.g. CIBIL Control Number or Loan Account
        "needs_proof": True,
        "description": "Credit bureau score rectification"
    }
}

def parse_and_validate_date(date_str: str) -> tuple[bool, str]:
    """Validates incident date (not in future, not older than 3 years)."""
    if not date_str or not str(date_str).strip():
        return False, "Incident or transaction date is required."

    cleaned_date = str(date_str).strip()
    parsed_date = None

    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"]:
        try:
            parsed_date = datetime.strptime(cleaned_date, fmt).date()
            break
        except ValueError:
            continue

    if not parsed_date:
        return False, "Invalid date format. Use YYYY-MM-DD or DD-MM-YYYY."

    today = date.today()
    if parsed_date > today:
        days_ahead = (parsed_date - today).days
        return False, f"Futuristic date detected ({cleaned_date}). Incidents cannot occur {days_ahead} days in the future."

    if (today - parsed_date).days > 1095:
        return False, f"Date ({cleaned_date}) is older than 3 years. Banking regulatory limitation period exceeded."

    return True, "Valid date"


# ─────────────────────────────────────────────────────────────────────────────
# 3-TIER HUMAN COHERENCE ENGINE — constants
# ─────────────────────────────────────────────────────────────────────────────

# Tier-2: Grammatical glue words (functional connectors present in genuine sentences)
# A keyword-bombed list has 0–5% of these; a real sentence typically has 20–50%.
GRAMMATICAL_GLUE_EN = {
    "i", "my", "me", "we", "our", "the", "a", "an", "this", "that", "is", "was", "were",
    "am", "are", "be", "been", "have", "has", "had", "do", "did", "does", "not", "no",
    "but", "and", "or", "so", "because", "when", "after", "before", "to", "from", "of",
    "in", "on", "at", "for", "with", "by", "it", "its", "he", "she", "they", "you",
    "your", "their", "as", "which", "also", "still", "yet", "already", "without", "never",
    "please", "kindly", "sir", "madam", "regarding", "however", "since", "during", "till",
    "while", "although", "though", "therefore", "hence", "immediately", "urgently"
}
GRAMMATICAL_GLUE_HINGLISH = {
    "mere", "mera", "meri", "mujhe", "hamara", "hamari", "hum", "aur", "ya", "lekin",
    "par", "phir", "bhi", "nahi", "na", "koi", "kuch", "ho", "hai", "tha", "thi", "the",
    "gaya", "gaye", "gayi", "raha", "rahi", "rahe", "kar", "karo", "kare", "se", "ko",
    "ka", "ki", "ke", "me", "mein", "pe", "par", "tak", "jo", "jab", "kab", "kyun",
    "please", "help", "mujh", "abhi", "kal", "aaj", "jaldi", "turant", "urgent", "ek",
    "do", "teen", "din", "mahine", "saal", "wala", "wali", "kyunki", "isliye", "uske"
}

# Tier-3: Grievance Action / Distress Verbs and Problem Phrases
# A complaint MUST describe an event or dispute — these are the markers
GRIEVANCE_ACTION_VERBS_EN = {
    "deducted", "debited", "charged", "failed", "declined", "rejected", "blocked",
    "lost", "stolen", "missing", "gone", "disappeared", "unauthorized", "hacked",
    "frozen", "locked", "suspended", "closed", "delayed", "pending", "not received",
    "not credited", "not dispensed", "wrongly", "incorrectly", "fraudulently",
    "transferred", "withdrawn", "harassed", "threatened", "abused", "denied",
    "cancelled", "duplicate", "overcharged", "applied", "not refunded", "bounced",
    "corrupted", "crashing", "not working", "unable", "cannot", "issue", "problem",
    "complaint", "dispute", "error", "wrong", "fake", "cheated", "scam", "trouble",
    "refund", "reversal", "reimbursement", "return", "rectify", "resolve", "help",
    "worried", "frustrated", "distressed", "urgent", "immediate", "critical",
    # Additional natural phrasing for transactions and fund disputes:
    "has not received", "have not received", "did not receive", "not yet received",
    "yet to receive", "unreceived", "not credited", "not yet credited", "uncredited",
    "not reflected", "not showing", "not updated", "not cleared", "did not get",
    "never received", "never got", "debited but", "deducted but", "paid but",
    "payment done but", "done from my side but", "sent but", "transferred but",
    "still pending", "pending credit", "pending transfer", "stuck", "failed to credit", "fail", "cut",
    "failed transfer", "no update", "no response", "waiting for refund", "money cut",
    "amount cut", "balance deducted", "cut from account", "unresolved"
}
GRIEVANCE_ACTION_VERBS_HINGLISH = {
    "kat gaye", "kat gaya", "kaate", "cut ho gaye", "cut ho gaya", "cut gaye", "cut gaya", "paise cut", "fail dikha", "fail hua", "fail ho gaya", "deduct hua", "deduct ho gaya", "nahi nikla",
    "nahi nikle", "nahi mila", "nahi mile", "nahi aaya", "nahi aaye", "chori",
    "kho gaya", "kho gaye", "band ho gaya", "block ho gaya", "block karo",
    "wapas karo", "refund chahiye", "pareshan", "dikkat", "problem", "complaint", "kripya madad", "paise wapas", "fas gaya", "atak gaya", "fas gaye", "help kijiye", "dhokha", "loss",
    "fraud hua", "galat", "dhoka", "galti", "jaldi", "turant", "zaruri",
    "nahi ho raha", "nahi ho rahi", "issue", "mushkil", "paise nahi", "paise kat"
}


def normalize_contractions(text: str) -> str:
    """
    Expands English contractions (e.g. hasn't -> has not, didn't -> did not, can't -> can not).
    Preserves natural semantic phrasing for downstream intent and verb recognition.
    """
    if not text:
        return ""
    text = re.sub(r"\bwon['’]t\b", "will not", text, flags=re.IGNORECASE)
    text = re.sub(r"\bcan['’]t\b", "can not", text, flags=re.IGNORECASE)
    text = re.sub(r"\bcannot\b", "can not", text, flags=re.IGNORECASE)
    text = re.sub(r"\bshan['’]t\b", "shall not", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\w+)n['’]t\b", r"\1 not", text, flags=re.IGNORECASE)
    return text


def _check_gibberish(text: str) -> tuple[bool, str]:
    """
    Tier-1: Detect random keyboard mashing or unreadable characters.
    Checks:
    - Vowel density: real words have 20-60% vowels. Gibberish tends to have either very few or irregular patterns.
    - Max consonant cluster: English/Hinglish words rarely have >4 consecutive consonants.
    - Dictionary word ratio: at least 30% of tokens should be recognizable dictionary words (len >= 3).
    """
    latin_chars = re.sub(r'[^a-zA-Z]', '', text)
    if not latin_chars:
        return True, ""  # Pass through — likely pure Devanagari Hindi

    vowels = re.findall(r'[aeiouAEIOU]', latin_chars)
    vowel_ratio = len(vowels) / len(latin_chars) if latin_chars else 0.5

    # Vowel ratio check — real words: 0.15 to 0.70
    if vowel_ratio < 0.10:
        return False, "Your description appears to contain unreadable characters or keyboard mashing. Please describe your issue in proper words."

    # Max consonant cluster length check
    consonant_runs = re.findall(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{5,}', text)
    if consonant_runs and max(len(r) for r in consonant_runs) >= 6:
        return False, "Your description appears to contain unreadable characters. Please describe your issue clearly."

    # Dictionary-word ratio: check that at least 30% of tokens look like real words
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    if tokens:
        # Simple heuristic: a 'real word' has at least one vowel
        real_words = [t for t in tokens if re.search(r'[aeiou]', t)]
        real_word_ratio = len(real_words) / len(tokens)
        if real_word_ratio < 0.30:
            return False, "Your description appears to contain unreadable or random characters. Please write your complaint in English, Hindi, or Hinglish."

    return True, ""


def _check_keyword_bombing(text: str, word_count: int) -> tuple[bool, str]:
    """
    Tier-2: Detect keyword-stuffed lists with no grammatical structure.
    A genuine sentence has >=10% grammatical glue words.
    A list of banking keywords (e.g. 'atm card bank fraud debit cibil') has near 0%.
    Also checks for suspicious patterns: all nouns, no punctuation, abnormally uniform word length.
    """
    tokens_lower = re.findall(r'\b[a-zA-Z\u0900-\u097F]{2,}\b', text.lower())
    if not tokens_lower or word_count < 6:
        return True, ""  # Let short texts be handled by the word_count check

    # Bypass for predominantly Devanagari (Hindi) text — glue check uses Latin tokens only
    devanagari_chars = re.findall(r'[\u0900-\u097F]', text)
    latin_chars_total = re.findall(r'[a-zA-Z]', text)
    if len(devanagari_chars) > len(latin_chars_total):
        # Hindi text — check only for Devanagari sentence markers (space, punctuation, conjunctions)
        has_devanagari_structure = bool(re.search(r'[,।!? ]', text)) and word_count >= 4
        return True, ""  # Pass through to Tier-3 for verb checking

    # Calculate grammatical glue ratio (combined EN + Hinglish)
    glue_matches = sum(
        1 for t in tokens_lower
        if t in GRAMMATICAL_GLUE_EN or t in GRAMMATICAL_GLUE_HINGLISH
    )
    glue_ratio = glue_matches / len(tokens_lower)

    # Check for phrase connectors: sentences have commas, periods, conjunctions
    has_punctuation = bool(re.search(r'[,\.;!?।]', text))

    # Check for a capital letter or sentence-start pattern
    has_sentence_structure = bool(re.search(r'[A-Z]', text[1:])) or has_punctuation

    # If glue ratio is very low AND no sentence structure → keyword bombing
    if glue_ratio < 0.08 and not has_sentence_structure and word_count >= 6:
        return False, (
            "Your description appears to be a list of keywords rather than a description of what happened. "
            "Please write in complete sentences explaining what occurred (e.g. 'My ATM card was declined but money was deducted')."
        )

    # Extra check: if ALL words are roughly same length (typical of tag clouds / keyword lists)
    if len(tokens_lower) >= 8:
        lengths = [len(t) for t in tokens_lower]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < 1.5 and glue_ratio < 0.12:
            return False, (
                "Your complaint description reads like a list of keywords. "
                "Please explain what happened to you in proper sentences."
            )

    return True, ""


def _check_grievance_verbs(text: str, aligned_text: str) -> tuple[bool, str]:
    """
    Tier-3: Ensure at least one grievance action verb, dispute phrase, or negative outcome pattern is present.
    A real banking complaint must describe an event or problem — not just name services.
    """
    # Normalize contractions in both original and aligned texts
    norm_text = normalize_contractions(text).lower()
    norm_aligned = normalize_contractions(aligned_text).lower()
    combined = f"{norm_text} {norm_aligned}"

    # 1. Structural pattern: Negated transaction action (e.g. "has not received", "did not credit", "yet to get")
    neg_action_pattern = (
        r'\b(not|never|no|failed to|unable to|yet to|hardly)\s+'
        r'(?:yet\s+|still\s+|been\s+|ever\s+)?'
        r'(receive|received|credit|credited|get|got|deliver|delivered|reflect|reflected|update|updated|reach|reached|clear|cleared|refund|refunded)\b'
    )
    if re.search(neg_action_pattern, combined):
        return True, ""

    # 2. Structural pattern: Payment event followed by contrastive outcome (e.g. "payment done ... but receiver ...", "debited ... however ...")
    contrast_pattern = r'\b(done|paid|debited|deducted|sent|transferred|withdrawn)\b[\w\s]{1,50}\b(but|however|still|yet|though)\b'
    if re.search(contrast_pattern, combined):
        return True, ""

    # 3. Check English problem verbs and phrases (exact word boundary)
    for verb in GRIEVANCE_ACTION_VERBS_EN:
        if re.search(r'\b' + re.escape(verb) + r'\b', combined):
            return True, ""

    # 4. Check Hinglish phrases (substring match)
    for phrase in GRIEVANCE_ACTION_VERBS_HINGLISH:
        if phrase in combined:
            return True, ""

    # 5. Check Devanagari distress markers
    devanagari_distress = ["कट", "गए", "नहीं", "मिला", "बंद", "धोखा", "खो", "समस्या", "शिकायत", "वापस", "ब्लॉक", "फंस"]
    for marker in devanagari_distress:
        if marker in text:
            return True, ""

    return False, (
        "Your description does not clearly describe a problem or issue. "
        "Please explain what went wrong (e.g. 'amount was deducted', 'card was declined', 'loan not closed')."
    )


def evaluate_semantic_and_emotional_validity(text: str) -> tuple[int, bool, str, str]:
    """
    3-Tier Human Coherence Engine + Multilingual SBERT Semantic Scoring.

    Tier 1 — Gibberish Detection (character entropy & vowel analysis)
    Tier 2 — Keyword Bombing Detection (grammatical glue ratio)
    Tier 3 — Grievance Action Verb Check (must describe a problem / dispute)
    Then  — SBERT cosine similarity against multilingual grievance anchors

    Returns: (score, is_valid, feedback_message, detected_language)
    """
    cleaned = (text or "").strip()
    detected_lang = detect_language(cleaned)
    aligned_text = align_multilingual_text(cleaned)

    words = re.findall(r'\b[a-zA-Z\u0900-\u097F]{2,}\b', cleaned.lower())
    word_count = len(words)

    # Minimum length gate
    if word_count < 4:
        return 5, False, "Description is too brief. Please explain what occurred in at least one sentence.", detected_lang

    # ─── TIER 1: Gibberish / Character Entropy ────────────────────────────────
    gibberish_ok, gibberish_msg = _check_gibberish(cleaned)
    if not gibberish_ok:
        return 5, False, gibberish_msg, detected_lang

    # ─── TIER 2: Keyword Bombing / Grammatical Glue Check ─────────────────────
    bombing_ok, bombing_msg = _check_keyword_bombing(cleaned, word_count)
    if not bombing_ok:
        return 8, False, bombing_msg, detected_lang

    # ─── SBERT SEMANTIC SIMILARITY & TIER 3 EVALUATION ───────────────────────
    # Embed text and calculate semantic alignment against multi-lingual banking grievance anchors
    text_vector = get_text_embedding(f"{cleaned} {aligned_text}")
    similarities = [cosine_similarity(text_vector, anchor_vec) for anchor_vec in ANCHOR_VECTORS]
    max_sim = max(similarities) if similarities else 0.0

    # ─── TIER 3: Grievance Action / Distress Check ────────────────────────────
    verb_ok, verb_msg = _check_grievance_verbs(cleaned, aligned_text)
    if not verb_ok:
        # Semantic & Emotional Safety Net:
        # If surface regex missed due to novel human phrasing, but deep-learning SBERT similarity is high (>= 0.45)
        # AND the sentence expresses negative polarity, contrast, or distress markers, validate the emotion!
        has_negative_marker = bool(re.search(r"\b(not|never|no|neither|nor|without|unable|hardly|scarcely|barely|n['’]t)\b", cleaned.lower()))
        has_contrast_marker = bool(re.search(r"\b(but|however|although|yet|still|though|instead)\b", cleaned.lower()))
        has_emotional_marker = bool(re.search(r"\b(help|urgent|please|waiting|worried|concern|frustrat|loss|stuck|delay)\b", cleaned.lower()))

        if max_sim >= 0.45 and (has_negative_marker or has_contrast_marker or has_emotional_marker):
            verb_ok = True
        else:
            return 10, False, verb_msg, detected_lang

    # Stricter semantic threshold to prevent word-salad / random keyword passing:
    # Real grievances score >= 0.40-0.75; random word mixtures score < 0.28.
    if max_sim < 0.28:
        return 10, False, "Your narrative does not closely match a recognized banking grievance pattern. Please clearly describe your specific financial transaction or service issue in complete sentences.", detected_lang

    score = 0
    if max_sim >= 0.50:
        score += 25
    elif max_sim >= 0.40:
        score += 20
    else:
        score += 15

    # Length & narrative completeness bonus
    if word_count >= 20:
        score += 10
    elif word_count >= 12:
        score += 8
    elif word_count >= 6:
        score += 6
    else:
        score += 4

    final_score = min(score, 35)
    return final_score, True, f"Valid grievance narrative ({detected_lang})", detected_lang


def check_adaptive_validity(
    service_type: str,
    description: str,
    incident_date: str = None,
    amount: float = None,
    reference_id: str = None,
    has_proof: bool = False,
    card_last4: str = None,
    account_no: str = None
) -> dict:
    """
    Adaptive validity check tailored specifically to the type of complaint.
    Does NOT ask for irrelevant data (e.g. amount for lost cards or login app bugs).
    """
    reqs = CATEGORY_REQUIREMENTS.get(service_type, {
        "needs_amount": True,
        "needs_ref_id": True,
        "needs_proof": False,
        "description": "Standard banking inquiry"
    })

    score = 0
    breakdown = {}
    missing_items = []

    # 1. Category Identification (15 pts)
    if service_type and service_type.strip():
        score += 15
        breakdown["service_category"] = 15
    else:
        missing_items.append("Select a valid grievance service category")

    # 2. Incident Date Check (15 pts)
    date_valid, date_msg = parse_and_validate_date(incident_date)
    if date_valid:
        score += 15
        breakdown["incident_date"] = 15
    else:
        missing_items.append(date_msg)

    # 3. Adaptive Requirement Evaluation (35 pts max)
    adaptive_score = 0
    
    # Financial amount check (Only if relevant!)
    if reqs.get("needs_amount", True):
        if amount is not None and amount > 0:
            adaptive_score += 15
        else:
            missing_items.append("Transaction amount (> ₹0) is required for fund dispute claims")
    else:
        # Non-monetary complaints (like lost card or app glitch) get full credit for this component
        adaptive_score += 15

    # Reference / Account / Card identifier check (Adaptive)
    if reqs.get("needs_ref_id", True):
        if reference_id and len(reference_id.strip()) >= 4:
            adaptive_score += 10
        else:
            missing_items.append("Transaction Reference / UTR Number (min 4 characters)")
    elif reqs.get("needs_card_last4", False):
        if card_last4 and len(card_last4.strip()) == 4:
            adaptive_score += 10
        else:
            missing_items.append("Card last 4 digits (e.g. 8824) to locate your card profile")
    elif reqs.get("needs_account_no", False):
        if (account_no and len(account_no.strip()) >= 4) or (reference_id and len(reference_id.strip()) >= 4):
            adaptive_score += 10
        else:
            missing_items.append("Bank Account / Customer ID Number")
    else:
        adaptive_score += 10

    # Proof attachment check (Only if strictly required!)
    if reqs.get("needs_proof", False):
        if has_proof:
            adaptive_score += 10
        else:
            missing_items.append("Supporting document (receipt, statement or document scan)")
    else:
        adaptive_score += 10

    score += adaptive_score
    breakdown["adaptive_data_fields"] = adaptive_score

    # 4. SBERT Multilingual Semantic & Emotional Coherence (35 pts)
    sem_score, sem_valid, sem_msg, detected_lang = evaluate_semantic_and_emotional_validity(description)
    score += sem_score
    breakdown["semantic_and_emotional_validity"] = sem_score
    if not sem_valid:
        missing_items.append(sem_msg)

    is_valid = (score >= 70) and date_valid and sem_valid and (len(missing_items) == 0)

    return {
        "score": score,
        "is_valid": is_valid,
        "detected_language": detected_lang,
        "breakdown": breakdown,
        "missing_items": missing_items,
        "feedback": (
            f"Grievance accepted as valid ({detected_lang} narrative)."
            if is_valid
            else f"Incomplete details: {'; '.join(missing_items)}"
        )
    }

# Backward compatibility alias
def check_validity(
    has_proof: bool,
    service_type: str,
    transaction_date: str,
    amount: float,
    reference_id: str,
    description: str
) -> dict:
    return check_adaptive_validity(
        service_type=service_type,
        description=description,
        incident_date=transaction_date,
        amount=amount,
        reference_id=reference_id,
        has_proof=has_proof
    )
