"""
multilingual_engine.py - Multilingual Complaint Analysis for Indian BFSI Redressal
Supports:
1. Multilingual text normalization (Hindi Devanagari, English, and Hinglish transliterated).
2. Semantic mapping of Indian banking expressions across languages:
   - "Mere account se paise kat gaye" (Hinglish)
   - "मेरे खाते से पैसे कट गए" (Hindi Devanagari)
   - "Money was deducted from my account" (English)
3. Language detection & translation alignment to standard BFSI grievance domains.
4. Multilingual semantic embeddings for cross-lingual duplicate and category matching.
"""

import re
import numpy as np

# Multilingual Banking Glossary mapping Hindi/Hinglish terms to standardized English BFSI terms
# This ensures that whether written in Hindi, Hinglish, or English, the semantic vectors align.
HINGLISH_TO_ENGLISH_MAP = {
    # Hindi Devanagari mappings
    r"\bखाते\b|\bखाता\b": "account",
    r"\bपैसे\b|\bरुपये\b|\bरुपया\b|\bरकम\b": "money funds balance",
    r"\bकट\s*गए\b|\bकट\s*गया\b|\bकटौती\b": "deducted debited",
    r"\bवापस\b|\bवापसी\b": "refund reversal",
    r"\bनहीं\s*मिला\b|\bनहीं\s*आए\b": "not received uncredited",
    r"\bधोखाधड़ी\b|\bधोखा\b": "fraud scam unauthorized",
    r"\bखो\s*गया\b|\bगुम\s*हो\s*गया\b": "lost stolen misplaced",
    r"\bबंद\b|\bब्लॉक\b": "blocked freeze closed",
    r"\bऋण\b|\bलोन\b": "loan emi",
    r"\bब्याज\b": "interest rate",
    r"\bशाखा\b": "branch",
    r"\bशिकायत\b": "complaint dispute",
    r"\bकार्ड\b": "card debit credit",
    r"\bअवैध\b|\bअनधिकृत\b": "unauthorized illegal",

    # Hinglish (Romanized Hindi) mappings
    r"\bmere\s+account\s+se\b|\bkhate\s+se\b": "from my bank account",
    r"\bpaise\s+kat\s+gaye\b|\bpaise\s+kat\s+gaya\b|\bmoney\s+kat\s+gaya\b|\bpaise\s+kat\s+gaye\b": "money debited without credit",
    r"\bkat\s+gaye\b|\bkat\s+gaya\b|\bkatt\s+gaya\b|\bkate\b": "deducted debited",
    r"\bpaise\b|\bpaisa\b|\brupaye\b|\brupay\b": "money amount funds",
    r"\bnahi\s+mila\b|\bnahi\s+aaya\b|\bnahi\s+aaye\b|\bnahe\s+mila\b": "not received uncredited",
    r"\bchori\s+ho\s+gaya\b|\bkho\s+gaya\b|\bgum\s+ho\s+gaya\b": "lost stolen misplaced",
    r"\bband\s+ho\s+gaya\b|\bblock\s+kar\s+do\b|\bblock\s+ho\s+gaya\b": "blocked frozen restricted",
    r"\bdhoka\b|\bfraud\s+hua\b|\bgoli\b": "fraud scam unauthorized",
    r"\bwaapas\b|\bwapas\b|\brefund\s+chahiye\b": "refund reversal credited back",
    r"\bjyada\s+charge\b|\bextra\s+charge\b|\bfaltu\s+charge\b": "unfair penalty excess charges",
    r"\bcall\s+karke\s+pareshan\b|\bdhamki\s+de\s+rahe\b": "harassment abusive threats recovery",
    r"\bpassbook\s+entry\b": "passbook statement record",
    r"\bkisi\s+aur\s+ko\s+chala\s+gaya\b": "transferred to wrong beneficiary",
    r"\batm\s+se\s+paise\s+nahi\s+nikle\b|\bcash\s+nahi\s+nikla\b": "atm cash not dispensed",
    r"\botp\s+nahi\s+bheja\b|\botp\s+bina\b": "without otp unauthorized"
}

def detect_language(text: str) -> str:
    """
    Detects if the grievance text is Hindi (Devanagari), Hinglish (Romanized), or English.
    """
    if not text:
        return "English"
    
    # Check for Devanagari Unicode block (0x0900 to 0x097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = max(len(re.findall(r'\w', text)), 1)
    
    if (devanagari_chars / total_chars) > 0.25:
        return "Hindi"
    
    # Check for common Hinglish marker words
    hinglish_markers = {
        "mere", "mera", "meri", "humara", "khate", "se", "paise", "kat", "gaye", "gaya",
        "nahi", "aaya", "aaye", "mila", "karo", "kijiye", "hua", "huye", "raha", "rahe",
        "bheja", "tha", "the", "thi", "bahut", "parso", "kal", "chahiye", "wapas", "dijiye",
        "kisi", "liya", "diya", "karke", "wala", "wali"
    }
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    hinglish_count = sum(1 for w in words if w in hinglish_markers)
    
    if hinglish_count >= 1 or (len(words) > 0 and (hinglish_count / len(words)) >= 0.10):
        return "Hinglish"
    
    return "English"

def align_multilingual_text(text: str) -> str:
    """
    Translates/normalizes Hindi and Hinglish banking expressions into standard
    BFSI semantic tokens while preserving the original context.
    Allows downstream models (TF-IDF, SVM, SBERT) to accurately process complaints
    in Hindi, Hinglish, and English identically.
    """
    if not text:
        return ""
    
    normalized = text
    for pattern, replacement in HINGLISH_TO_ENGLISH_MAP.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
    return normalized

def extract_multilingual_semantic_vector(text: str) -> np.ndarray:
    """
    Produces language-invariant dense vector using aligned semantic representation.
    """
    from semantic_engine import get_text_embedding
    aligned = align_multilingual_text(text)
    # Combine original and aligned for maximum recall
    composite_text = f"{text} {aligned}"
    return get_text_embedding(composite_text)
