import sqlite3
import random
from datetime import datetime, timedelta

DB_PATHS = [
    r'G:\Mini_project\Python_codes\grievanceiq.db',
    r'G:\Mini_project\Dataset\grievanceiq.db'
]

KB_ARTICLES = [
    (1, 1, 'Failed UPI Transaction Auto-Reversal (NPCI TAT)', 'Digital & UPI Banking',
     'upi,imps,gpay,phonepe,paytm,failed,debited,timeout',
     '1. Verify NPCI switch UTR status in CBS.\n2. 92% of network timeouts auto-revert within T+1 day.\n3. If unreversed after 48h, initiate interbank chargeback with auto-compensation ₹100/day per RBI circular.',
     'RBI/DPSS/2019-20/67 Circular on Harmonisation of TAT', 1, 1),
    (2, 2, 'Credit Card Disputed Surcharge & Fraud Reversal', 'Cards & ATM Services',
     'credit card,surcharge,disputed,fraud,unauthorized,pos,swipe',
     '1. Emergency hotlist card globally across POS/E-commerce.\n2. Obtain signed dispute declaration form.\n3. Grant temporary shadow credit within 72h under RBI zero liability framework.',
     'RBI Master Direction - Credit Card Issuance 2022', 1, 1),
    (3, 2, 'ATM Cash Dispense Failure Journal Reconciliation', 'Cards & ATM Services',
     'atm,cash,dispense,failed,journal,not dispensed,ej log',
     '1. Extract Electronic Journal (EJ) and cash sensor audit logs.\n2. Confirm dispenser purge/jam status code.\n3. Apply CBS auto-credit AR-ATM within T+5 days with ₹100/day penalty for delay.',
     'RBI DPSS Circular DPSS.PD.No.2632/02.10.002/2010-2011', 1, 1),
    (4, 3, 'Loan Closure NOC & Property Document Release Protocol', 'Loans & Advances',
     'loan,noc,foreclosure,property documents,mortgage,closure',
     '1. Verify full loan balance closure and interest amortization.\n2. Trigger central archival vault dispatch of original property deeds within 30 days.\n3. Issue Digitally Signed NOC Certificate and update CIBIL status to CLOSED.',
     'RBI Circular DoR.MCS.REC.38/01.01.001/2023-24', 1, 1),
    (5, 1, 'KYC Periodic Update & Account Freeze Unblocking', 'Account & Branch Operations',
     'kyc,freeze,unblock,re-kyc,pan,aadhaar,cams,ckyc',
     '1. Scrutinize C-KYC repository and Aadhaar XML verification.\n2. If documents are genuine, lift debit freeze immediately within 4 hours.\n3. Send SMS and email confirmation to account holder.',
     'RBI Master Direction - Know Your Customer (KYC) Direction 2016', 1, 1),
    (6, 3, 'CIBIL / Credit Bureau Dispute Correction Protocol', 'Credit Bureau Liaison',
     'cibil,experian,crif,score,inaccurate,overdue,dispute',
     '1. Cross-reference loan repayment statement against bureau bureau data.\n2. Identify misreported DPD (Days Past Due) tags.\n3. Upload Bureau Correction File (BCF) within 21 days per RBI mandate.',
     'Credit Information Companies (Regulation) Act 2005', 1, 1),
    (7, 2, 'Emergency Lost / Stolen Card Global Hotlisting', 'Cards & ATM Services',
     'lost card,stolen card,block,hotlist,replacement,atm skim',
     '1. Immediately send ISO-8583 0420 advice to disable card on host switch.\n2. Issue confirmation SMS and dispatch contactless EMV replacement card.\n3. Zero customer liability applies from the exact second of reporting.',
     'RBI/2017-18/15 DBR.No.Leg.BC.78/09.07.005/2017-18', 1, 1),
    (8, 1, 'Pensioner Life Certificate & Jeevan Pramaan Processing', 'Retail Banking Team',
     'pension,jeevan pramaan,life certificate,senior citizen,sparsh',
     '1. Verify biometric authentication via Jeevan Pramaan / UIDAI gateway.\n2. Update CPPC (Central Pension Processing Centre) record.\n3. Ensure pension disbursement continues without interruption.',
     'RBI Circular on Pension Disbursement to Central / State Pensioners', 1, 1)
]

AUDIT_LOG_TEMPLATES = [
    ('customer', 'SUBMIT_COMPLAINT', 'complaint', 'Customer submitted grievance with supporting documentary proof.'),
    ('ai_bot', 'AI_AUTONOMOUS_RESOLVE', 'complaint', 'Nova-AI resolved grievance autonomously based on high confidence (>92%) and valid evidence.'),
    ('officer', 'STATUS_CHANGE', 'complaint', 'Officer Pooja Sharma reviewed case and moved status from pending to in_progress.'),
    ('officer', 'VERIFY_EVIDENCE', 'complaint', 'Supporting PDF receipt verified against NPCI core switch records.'),
    ('officer', 'SUBMIT_RESOLUTION', 'complaint', 'Formal Statutory Resolution Memorandum issued with refund settlement UTR.'),
    ('system', 'SLA_MONITOR', 'complaint', 'Automated SLA monitor evaluated deadline compliance; no breach detected.'),
    ('ai_bot', 'NLP_CATEGORY_ROUTE', 'complaint', 'Nova NLP classifier routed complaint to Cards & ATM Services with 96.4% confidence.'),
    ('admin', 'UPDATE_KB_POLICY', 'kb_article', 'Admin updated turnaround time policy in accordance with RBI revised circular.'),
    ('officer', 'ADD_NOTE', 'complaint', 'Officer noted: Beneficiary bank switch confirmed refund return file generated.'),
    ('system', 'DOCUMENT_OCR_SCRUTINY', 'complaint', 'AI OCR engine scanned evidence slip: extracted UTR and amount with 99.2% match.')
]

def reseed(db_path):
    print(f"Reseeding {db_path}...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 1. Clear existing complaints and dependent tables
    c.execute("DELETE FROM status_history")
    c.execute("DELETE FROM resolutions")
    c.execute("DELETE FROM investigation_notes")
    c.execute("DELETE FROM complaint_messages")
    c.execute("DELETE FROM feedback")
    c.execute("DELETE FROM audit_logs")
    c.execute("DELETE FROM knowledge_base_articles")
    c.execute("DELETE FROM complaints")

    # 2. Insert Knowledge Base Articles
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    for art in KB_ARTICLES:
        c.execute('''
            INSERT INTO knowledge_base_articles 
            (article_id, department_id, title, category, keywords, guidance_steps, regulatory_reference, can_self_resolve, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (art[0], art[1], art[2], art[3], art[4], art[5], art[6], art[7], art[8], now_str, now_str))

    # 3. Generate 380 Realistic Complaints
    banks = [
        (1, 'State Bank of India (SBI)'),
        (2, 'HDFC Bank'),
        (3, 'ICICI Bank'),
        (4, 'Axis Bank'),
        (5, 'Punjab National Bank (PNB)')
    ]
    
    depts = [
        (1, 'Retail Banking Team'),
        (2, 'Card Disputes Team'),
        (3, 'Loan Servicing Team')
    ]

    proofs = [
        ('uploads/samples/icici_upi_payment_failed.png', 'icici_upi_payment_failed.pdf'),
        ('uploads/samples/hdfc_credit_card_fraud.png', 'hdfc_credit_card_fraud.pdf'),
        ('uploads/samples/sbi_atm_dispense_error.png', 'sbi_atm_dispense_error.pdf'),
        ('uploads/samples/axis_loan_foreclosure_noc.png', 'axis_loan_foreclosure_noc.pdf'),
        ('uploads/samples/pnb_kyc_compliance_slip.png', 'pnb_kyc_compliance_slip.pdf'),
    ]

    services_by_dept = {
        1: [
            ('Digital & UPI Banking', 'Failed UPI payment of INR {amt} debited but beneficiary not credited. Ref UTR: {ref}.', 1),
            ('Account & Branch Operations', 'Account placed on temporary debit freeze despite submitting re-KYC documents. Reference: {ref}.', 5),
            ('Retail Banking Team', 'Unauthorized SMS alert fee and hidden charges debited from savings account. Ref: {ref}.', 8)
        ],
        2: [
            ('Cards & ATM Services', 'ATM at {branch} deducted INR {amt} from account but cash was not dispensed. ATM Ref: {ref}.', 3),
            ('Card Disputes Team', 'Fraudulent overseas POS transaction charged on credit card ending {ref}. Surcharge disputed INR {amt}.', 2),
            ('Cards & ATM Services', 'Emergency card block requested for lost debit card ending {ref}. Please issue replacement card.', 7)
        ],
        3: [
            ('Loans & Advances', 'Full loan repayment completed for loan account {ref}. NOC and original deeds not released after 35 days.', 4),
            ('Loan Servicing Team', 'Excess interest and penal charges debited post loan restructuring for loan {ref}. Amount INR {amt}.', 4),
            ('Credit Bureau Liaison', 'CIBIL report incorrectly showing overdue status for already closed two-wheeler loan {ref}.', 6)
        ]
    }

    officers = {1: 9, 2: 10, 3: 11} # Pooja (dept 1), Rahul (dept 2), Vikram (dept 3)
    
    complaint_records = []
    audit_records = []

    for i in range(1, 381):
        token = f"GRV-2026-{i:05d}"
        bank_id, bank_name = random.choice(banks)
        dept_id, dept_name = random.choice(depts)
        service_tuple = random.choice(services_by_dept[dept_id])
        service_type, desc_tmpl, kb_id = service_tuple

        amt = random.choice([500.0, 1200.0, 2450.0, 5000.0, 8500.0, 10000.0, 15000.0, 25000.0, 45000.0, None])
        ref_id = f"REF{random.randint(10000000, 99999999)}"
        branch = random.choice(['Nariman Point, Mumbai', 'Connaught Place, New Delhi', 'Indiranagar, Bangalore', 'Banjara Hills, Hyderabad', 'Park Street, Kolkata', 'T Nagar, Chennai'])
        description = desc_tmpl.format(amt=amt or 0, ref=ref_id, branch=branch)

        proof_png, proof_pdf = random.choice(proofs)
        proof_file = random.choice([proof_png, f"uploads/samples/{proof_pdf}"])

        # ~57% BOT autonomous resolved, ~43% HUMAN queued
        is_bot = (random.random() < 0.57)

        days_ago = random.randint(1, 45)
        created_time = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(1, 20), minutes=random.randint(0, 59))
        created_str = created_time.strftime('%Y-%m-%d %H:%M:%S')

        priority = random.choice(['High', 'High', 'Medium', 'Medium', 'Medium', 'Low'])
        validity_score = random.randint(85, 100) if is_bot else random.randint(65, 95)
        bot_confidence = round(random.uniform(0.91, 0.99), 2) if is_bot else round(random.uniform(0.55, 0.88), 2)

        if is_bot:
            status = 'resolved'
            resolution_mode = 'BOT'
            assigned_officer = None
            resolved_time = created_time + timedelta(seconds=random.randint(12, 180)) # Solved in under 3 mins!
            resolved_str = resolved_time.strftime('%Y-%m-%d %H:%M:%S')
            resolution_notes = (
                f"Autonomous Nova-AI Redressal Order [RBI-SOP-{kb_id:03d}]: Disputed transaction verified with {bank_name} core switch. "
                f"Full adjustment of INR {amt or 0:,.2f} credited to customer account under statutory turnaround regulations. Settlement UTR: REV-{ref_id}."
            )
            evidence_status = 'VERIFIED'
            evidence_verified_by = None
            evidence_verified_at = created_str
        else:
            resolution_mode = 'HUMAN'
            assigned_officer = officers.get(dept_id, 9)
            # Mix of pending, in_progress, under_review, resolved
            status_choice = random.choice(['pending', 'in_progress', 'under_review', 'resolved', 'resolved'])
            status = status_choice
            evidence_status = random.choice(['VERIFIED', 'VERIFIED', 'PENDING_REVIEW', 'REJECTED'])
            evidence_verified_by = assigned_officer if evidence_status in ['VERIFIED', 'REJECTED'] else None
            evidence_verified_at = created_str if evidence_status in ['VERIFIED', 'REJECTED'] else None
            if status == 'resolved':
                resolved_time = created_time + timedelta(hours=random.randint(4, 48))
                resolved_str = resolved_time.strftime('%Y-%m-%d %H:%M:%S')
                resolution_notes = f"Resolution verified by Grievance Officer. Reversal UTR: SETTL-{ref_id}. Bank customer communication sent."
            else:
                resolved_str = None
                resolution_notes = None

        sla_deadline = created_time + timedelta(days=3)
        sla_deadline_str = sla_deadline.strftime('%Y-%m-%d %H:%M:%S')
        sla_breached = 1 if (status != 'resolved' and datetime.utcnow() > sla_deadline) else 0

        c.execute('''
            INSERT INTO complaints (
                complaint_id, token, company_id, department_id, submitted_at, raw_text,
                state, service_type, transaction_date, amount, reference_id, branch,
                description, proof_file_path, custom_fields, priority, status,
                validity_score, validity_status, resolution_mode, matched_article_id,
                bot_confidence, escalation_level, current_assigned_officer_id,
                escalated_at, escalation_reason, sla_deadline, sla_breached,
                resolved_at, resolution_notes, reopen_count, can_reopen_until,
                created_at, updated_at, customer_id, sub_category, evidence_status,
                evidence_verified_by, evidence_verified_at, evidence_rejection_reason
            ) VALUES (
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?
            )
        ''', (
            i, token, bank_id, dept_id, created_str, description,
            'Maharashtra', service_type, created_time.strftime('%Y-%m-%d'), amt, ref_id, branch,
            description, proof_file, None, priority, status,
            validity_score, 'VALID', resolution_mode, kb_id,
            bot_confidence, 0, assigned_officer,
            None, None, sla_deadline_str, sla_breached,
            resolved_str, resolution_notes, 0, None,
            created_str, created_str, 4, service_type, evidence_status,
            evidence_verified_by, evidence_verified_at, 'Missing legible UTR signature' if evidence_status == 'REJECTED' else None
        ))

    # 4. Insert 35 Realistic Audit Logs
    for log_id in range(1, 36):
        tmpl = random.choice(AUDIT_LOG_TEMPLATES)
        actor_type, action, entity_type, base_details = tmpl
        comp_num = random.randint(1, 380)
        target_token = f"GRV-2026-{comp_num:05d}"
        details = f"[{target_token}] {base_details}"
        log_time = datetime.utcnow() - timedelta(hours=random.randint(1, 120), minutes=random.randint(0, 59))
        log_time_str = log_time.strftime('%Y-%m-%d %H:%M:%S')
        actor_id = 9 if actor_type == 'officer' else (6 if actor_type == 'admin' else None)

        c.execute('''
            INSERT INTO audit_logs (log_id, actor_type, actor_id, action, entity_type, entity_id, details, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (log_id, actor_type, actor_id, action, entity_type, target_token, details, log_time_str))

    conn.commit()
    conn.close()
    print(f"Successfully reseeded {db_path} with 380 complaints, 8 KB articles, and 35 audit logs.")

if __name__ == '__main__':
    for path in DB_PATHS:
        try:
            reseed(path)
        except Exception as e:
            print(f"Error reseeding {path}: {e}")
