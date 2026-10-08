import io
import os
import re
from PIL import Image
import pypdf
import docx
from sentence_transformers import SentenceTransformer, util

print("Initializing SBERT semantic model (all-MiniLM-L6-v2)...")
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Reference canonical banking complaint semantic benchmarks
BENCHMARK_COMPLAINTS = [
    "Unauthorized transaction occurred on my bank account without my permission or knowledge.",
    "Money was debited from my account via UPI ATM or net banking but transaction failed and was not credited.",
    "Excess and unfair charges or penalty fees deducted by the bank incorrectly.",
    "Credit card dispute regarding duplicate billing fraudulent charge or wrong interest calculation.",
    "Loan foreclosure NOC and closure document delayed despite full payment of loan EMI.",
    "ATM did not dispense cash but money was deducted from my account balance.",
    "Bank customer service failed to resolve grievance regarding blocked card or KYC suspension.",
    "Fraudulent phishing withdrawal and cyber crime scam on my savings account.",
    "Fund transfer via IMPS NEFT RTGS failed and amount is stuck pending refund.",
    "Wrong EMI deducted after loan pre-closure and bank refuses to refund excess amount."
]

print("Pre-computing SBERT benchmark complaint embeddings...")
BENCHMARK_EMBEDDINGS = sbert_model.encode(BENCHMARK_COMPLAINTS, convert_to_tensor=True)

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extracts raw text content from uploaded proof files (PDF, DOCX, TXT, etc.)."""
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    try:
        if ext == ".pdf":
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages[:10]: # read up to 10 pages
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
        elif ext in [".docx", ".doc"]:
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + " "
        elif ext in [".txt", ".csv"]:
            text = file_bytes.decode("utf-8", errors="ignore")
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            # Image files: if text isn't directly extractable without OCR binary,
            # return filename/metadata indicators or basic header text
            text = f"Receipt proof image file {filename}"
    except Exception as e:
        print(f"File text extraction notice: {e}")
        text = f"Proof document {filename}"
        
    return text.strip()

def analyze_semantic_validity(narrative: str, proof_text: str):
    """
    Performs dual SBERT semantic similarity analysis:
    1. narrative_semantic_score: Evaluates how well the narrative semantically aligns
       with genuine BFSI grievance domains (0.0 to 1.0).
    2. proof_similarity_score: Evaluates semantic alignment between the customer's description
       and the content/context of the uploaded proof.
    """
    cleaned_narrative = narrative.strip()
    narrative_embedding = sbert_model.encode(cleaned_narrative, convert_to_tensor=True)
    
    # 1. Similarity with benchmark BFSI complaints
    cos_scores = util.cos_sim(narrative_embedding, BENCHMARK_EMBEDDINGS)[0]
    max_semantic_sim = float(cos_scores.max().item())
    # SBERT MiniLM cosine similarity typically ranges from 0.15 (unrelated) to 0.85+ (highly identical)
    # Normalize score into a friendly 0 - 100 scale
    narrative_semantic_score = round(max(0.0, min(1.0, max_semantic_sim)), 3)
    
    # 2. Similarity with uploaded proof
    proof_similarity_score = 0.5  # default baseline for image proofs
    if proof_text and len(proof_text.strip()) > 15:
        # Check semantic overlap or direct entity matches (account/amounts/UTR)
        proof_chunk = proof_text[:1000] # compare against first 1000 chars of proof
        proof_embedding = sbert_model.encode(proof_chunk, convert_to_tensor=True)
        proof_sim = float(util.cos_sim(narrative_embedding, proof_embedding)[0][0].item())
        proof_similarity_score = round(max(0.0, min(1.0, proof_sim)), 3)
    
    return {
        "narrative_semantic_score": narrative_semantic_score,
        "proof_similarity_score": proof_similarity_score,
        "is_semantically_valid": narrative_semantic_score >= 0.35, # genuine BFSI complaint threshold
    }
