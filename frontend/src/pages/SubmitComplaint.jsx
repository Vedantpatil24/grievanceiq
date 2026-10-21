import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { 
  ShieldAlert, CheckCircle, AlertTriangle, FileText, 
  ArrowRight, Upload, Building2, HelpCircle, CreditCard, 
  Smartphone, IndianRupee, Landmark, Clock, FileCheck
} from 'lucide-react';

const SERVICE_CONFIGS = {
  "UPI / IMPS / Digital Fund Transfer": {
    label: "UPI / IMPS / Digital Fund Transfer",
    categoryGroup: "Payments & Transfers",
    needsAmount: true,
    amountLabel: "Disputed Transaction Amount (INR) *",
    needsRef: true,
    refLabel: "12-Digit UPI Ref / UTR / Transaction ID *",
    refPlaceholder: "e.g. 409823149812 or UTR-982314",
    needsCard4: false,
    needsAccountNo: false,
    needsProof: true,
    proofLabel: "Payment Confirmation Receipt / Bank Statement Scan * (Mandatory)",
    proofHint: "Screenshot of failed UPI payment, debit SMS confirmation, or passbook entry (JPG, PNG, PDF).",
    descriptionHint: "Describe transaction flow: sender VPA, receiver VPA, app used (Google Pay, PhonePe, Paytm), and error message."
  },
  "Lost / Stolen Card & Emergency Block": {
    label: "Lost / Stolen Card & Emergency Block",
    categoryGroup: "Card Security & Hotlisting",
    needsAmount: false,
    amountLabel: "Disputed Charges (Optional - Leave blank if none)",
    needsRef: false,
    needsCard4: true,
    card4Label: "Card Last 4 Digits * (e.g. 8824)",
    card4Placeholder: "4 digits only (e.g. 8824)",
    needsAccountNo: false,
    needsProof: false,
    proofLabel: "Supporting Document (Optional - e.g. Police complaint / GD copy)",
    proofHint: "Not mandatory. If you lodged an online loss report, upload a copy here.",
    descriptionHint: "State date, approximate time, and city where card was lost or misplaced, and confirm whether you request immediate hotlisting."
  },
  "Credit Card / Disputed Charges & Fee": {
    label: "Credit Card / Disputed Charges & Fee",
    categoryGroup: "Cards & Billing",
    needsAmount: true,
    amountLabel: "Billed Disputed Amount (INR) *",
    needsRef: true,
    refLabel: "Statement Reference or Disputed Transaction ID *",
    refPlaceholder: "e.g. TXN-CARD-8839120",
    needsCard4: true,
    card4Label: "Card Last 4 Digits *",
    card4Placeholder: "e.g. 4912",
    needsAccountNo: false,
    needsProof: true,
    proofLabel: "Credit Card Statement Copy / Charge Invoice * (Mandatory)",
    proofHint: "Attach monthly statement highlighting the disputed charge or fee.",
    descriptionHint: "Specify whether charge is an unauthorized swipe, duplicate billing, annual fee dispute, or dynamic currency conversion."
  },
  "ATM Cash Withdrawal Failure": {
    label: "ATM Cash Withdrawal Failure",
    categoryGroup: "ATM & Cash Dispense",
    needsAmount: true,
    amountLabel: "Un-dispensed Debited Amount (INR) *",
    needsRef: true,
    refLabel: "ATM Transaction Reference / ATM ID *",
    refPlaceholder: "e.g. ATM-TXN-882190 or Machine ID S1NA0012",
    needsCard4: false,
    needsAccountNo: false,
    needsProof: false,
    proofLabel: "ATM Slip / Account Statement (Optional)",
    proofHint: "If ATM dispensed a failure slip or mini-statement, attach image here.",
    descriptionHint: "Include ATM location/address, bank of ATM used, debit SMS timestamp, and exact cash amount dispensed (if partial)."
  },
  "Net Banking / Mobile App & Tech Glitch": {
    label: "Net Banking / Mobile App & Tech Glitch",
    categoryGroup: "Digital Channels",
    needsAmount: false,
    amountLabel: "Impacted Amount (Optional - Leave blank if technical access issue)",
    needsRef: false,
    needsCard4: false,
    needsAccountNo: true,
    accountNoLabel: "Net Banking User ID / Customer ID / Account No *",
    accountNoPlaceholder: "e.g. CUST-901824 or Account No",
    needsProof: false,
    proofLabel: "App Error Screenshot (Optional)",
    proofHint: "Attach screenshot showing error code, app crash, or authentication timeout.",
    descriptionHint: "Provide device model, app version / browser type, operating system (Android / iOS / Windows), and error description."
  },
  "KYC, Account Freezing & Dormancy": {
    label: "KYC, Account Freezing & Dormancy",
    categoryGroup: "Account Operations",
    needsAmount: false,
    amountLabel: "Frozen Balance (Optional)",
    needsRef: false,
    needsCard4: false,
    needsAccountNo: true,
    accountNoLabel: "Savings / Current Account Number *",
    accountNoPlaceholder: "e.g. 50100294819284",
    needsProof: true,
    proofLabel: "KYC Document / ID Proof / Passbook Copy * (Mandatory)",
    proofHint: "Upload Aadhaar, PAN card, or bank passbook copy for identity verification.",
    descriptionHint: "Explain when the account was frozen, branch where KYC was submitted, and any communication received from bank."
  },
  "Loan Closure, NOC & Document Dispatch": {
    label: "Loan Closure, NOC & Document Dispatch",
    categoryGroup: "Loans & Lending",
    needsAmount: false,
    amountLabel: "Final Settlement Paid (INR) (Optional)",
    needsRef: true,
    refLabel: "Loan Account Number (LAN) *",
    refPlaceholder: "e.g. HL-MUM-2021-99824",
    needsCard4: false,
    needsAccountNo: false,
    needsProof: true,
    proofLabel: "Final Payment Receipt / Closure Statement * (Mandatory)",
    proofHint: "Upload loan repayment clearance receipt or bank acknowledgement.",
    descriptionHint: "State loan product (Home Loan, Auto Loan, Personal Loan), date of final repayment, and pending documents (NOC, Title Deeds)."
  },
  "Credit Bureau / CIBIL Rectification": {
    label: "Credit Bureau / CIBIL Rectification",
    categoryGroup: "Credit Reporting",
    needsAmount: false,
    amountLabel: "Disputed Overdue Balance Shown (Optional)",
    needsRef: true,
    refLabel: "CIBIL Control Number (ECN) or Loan Account No *",
    refPlaceholder: "e.g. ECN-88491024 or Account No",
    needsCard4: false,
    needsAccountNo: false,
    needsProof: true,
    proofLabel: "CIBIL / Experian Credit Report Page * (Mandatory)",
    proofHint: "Attach CIR report snippet highlighting the erroneous DPD, write-off, or settled status.",
    descriptionHint: "Explain the discrepancy (e.g. loan closed but showing overdue, identity mix-up, or delayed reporting by bank)."
  },
  "Staff Behavior & Recovery Harassment": {
    label: "Staff Behavior & Recovery Harassment",
    categoryGroup: "Conduct & Fair Practice Code",
    needsAmount: false,
    amountLabel: "Claimed Overdue Amount (Optional)",
    needsRef: false,
    needsCard4: false,
    needsAccountNo: true,
    accountNoLabel: "Account Number / Customer ID / Reference *",
    accountNoPlaceholder: "e.g. ACC-881923 or Mobile No",
    needsProof: false,
    proofLabel: "Call Log Screenshot / Audio / SMS Notice (Optional)",
    proofHint: "Attach call logs or messages violating RBI fair practice timing codes (7 AM - 7 PM).",
    descriptionHint: "Specify agent or employee name, branch or agency, dates, call timings, and nature of misconduct."
  }
};

export default function SubmitComplaint() {
  const { lang, t } = useLanguage();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [missingItems, setMissingItems] = useState([]);

  // Form inputs
  const [companyId, setCompanyId] = useState('');
  const [serviceType, setServiceType] = useState('UPI / IMPS / Digital Fund Transfer');
  const [transactionDate, setTransactionDate] = useState('');
  const [amount, setAmount] = useState('');
  const [referenceId, setReferenceId] = useState('');
  const [cardLast4, setCardLast4] = useState('');
  const [accountNo, setAccountNo] = useState('');
  const [branch, setBranch] = useState('');
  const [description, setDescription] = useState('');
  const [proofFile, setProofFile] = useState(null);

  // Real-time document validation
  const [docValidating, setDocValidating] = useState(false);
  const [docWarnings, setDocWarnings] = useState([]);
  const [docValid, setDocValid] = useState(null); // null = not checked, true = ok, false = warnings

  // Result state after submission
  const [submittedData, setSubmittedData] = useState(null);
  const [decisionLoading, setDecisionLoading] = useState(false);
  const [decisionFinished, setDecisionFinished] = useState(null);

  const activeConfig = SERVICE_CONFIGS[serviceType] || SERVICE_CONFIGS["UPI / IMPS / Digital Fund Transfer"];

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    setProofFile(file || null);
    setDocWarnings([]);
    setDocValid(null);

    if (!file) return;

    setDocValidating(true);
    try {
      const fd = new FormData();
      fd.append('proof_file', file);
      fd.append('service_type', serviceType);
      const selectedCompany = companies.find(c => String(c.company_id) === String(companyId));
      if (selectedCompany) fd.append('submitted_bank', selectedCompany.company_name);
      if (transactionDate) fd.append('submitted_date', transactionDate);
      if (amount) fd.append('submitted_amount', amount);
      if (referenceId) fd.append('submitted_ref_id', referenceId);
      if (branch) fd.append('submitted_branch', branch);

      const res = await axios.post('/api/validate-document', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setDocValid(res.data.valid);
      setDocWarnings(res.data.warnings || []);
    } catch (err) {
      // If endpoint fails, don't block user
      setDocValid(true);
    } finally {
      setDocValidating(false);
    }
  };


  useEffect(() => {
    axios.get('/api/companies')
      .then(res => {
        setCompanies(res.data);
        if (res.data.length > 0) setCompanyId(res.data[0].company_id);
      })
      .catch(err => console.error('Error fetching companies:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setMissingItems([]);
    setLoading(true);

    const formData = new FormData();
    formData.append('company_id', companyId);
    formData.append('service_type', serviceType);
    formData.append('transaction_date', transactionDate);
    formData.append('description', description);
    formData.append('branch', branch || 'Main Branch');

    if (activeConfig.needsAmount && amount) {
      formData.append('amount', amount);
    } else if (amount) {
      formData.append('amount', amount);
    }

    if (activeConfig.needsRef && referenceId) {
      formData.append('reference_id', referenceId);
    }

    if (activeConfig.needsCard4 && cardLast4) {
      formData.append('card_last4', cardLast4);
    }

    if (activeConfig.needsAccountNo && accountNo) {
      formData.append('account_no', accountNo);
    }

    const storedUser = JSON.parse(localStorage.getItem('grievanceiq_user') || '{}');
    if (storedUser && storedUser.user_id) {
      formData.append('customer_id', storedUser.user_id);
    }

    if (proofFile) {
      formData.append('proof_file', proofFile);
    }

    try {
      const res = await axios.post('/api/complaints/submit', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSubmittedData(res.data);
    } catch (err) {
      if (err.response && err.response.status === 422) {
        const detail = err.response.data.detail;
        setErrorMsg(detail.feedback || 'Complaint score is below required threshold.');
        setMissingItems(detail.missing_items || []);
      } else {
        setErrorMsg(err.response?.data?.detail || 'An unexpected error occurred during submission.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerDecision = async (decision) => {
    if (!submittedData?.token) return;
    setDecisionLoading(true);

    try {
      const res = await axios.post(`/api/complaints/${submittedData.token}/customer-decision`, {
        decision: decision,
        feedback_notes: decision === 'SOLVED' ? 'Customer accepted the provided resolution guidance.' : 'Customer requested escalation to a grievance redressal officer.'
      });
      setDecisionFinished({
        decision,
        message: res.data.message,
        officer: res.data.assigned_officer,
        sla: res.data.sla_deadline
      });
    } catch (err) {
      alert('Error updating complaint decision: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDecisionLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '960px' }}>
      {/* INSTITUTIONAL PORTAL BANNER */}
      <div style={{ 
        background: 'linear-gradient(135deg, #0f2942 0%, #1e3a8a 100%)', 
        borderRadius: '12px', 
        padding: '28px 32px', 
        color: '#ffffff', 
        marginBottom: '28px',
        boxShadow: '0 4px 14px rgba(15, 23, 42, 0.12)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <Landmark size={28} color="#93c5fd" />
          <span style={{ fontSize: '0.85rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#93c5fd' }}>
            Banking Consumer Redressal Forum | Reserve Bank Ombudsman Framework
          </span>
        </div>
        <h1 style={{ fontSize: '1.9rem', fontWeight: '800', margin: '4px 0 8px 0', letterSpacing: '-0.02em' }}>
          {t('submit_title')}
        </h1>
        <p style={{ color: '#cbd5e1', fontSize: '0.975rem', maxWidth: '780px', lineHeight: '1.5' }}>
          {t('submit_subtitle')}
        </p>

        {/* MULTILINGUAL CALLOUT BADGE */}
        <div style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '8px', 
          marginTop: '16px', 
          background: 'rgba(255, 255, 255, 0.12)', 
          padding: '6px 14px', 
          borderRadius: '9999px',
          fontSize: '0.825rem',
          color: '#e2e8f0',
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <span style={{ fontWeight: '700', color: '#60a5fa' }}>Multilingual Support:</span>
          <span>Complaints accepted in English, Hindi (हिंदी), and Hinglish.</span>
        </div>
      </div>

      {/* ERROR / VALIDITY REJECTION BANNER */}
      {errorMsg && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '10px', padding: '20px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#991b1b', fontWeight: '700', fontSize: '1rem' }}>
            <AlertTriangle size={22} />
            <span>Complaint Quality Verification Notice</span>
          </div>
          <p style={{ color: '#7f1d1d', marginTop: '8px', fontSize: '0.925rem', lineHeight: '1.5' }}>{errorMsg}</p>
          {missingItems.length > 0 && (
            <div style={{ marginTop: '12px', background: '#ffffff', borderRadius: '6px', padding: '12px 16px', border: '1px solid #fee2e2' }}>
              <div style={{ fontSize: '0.825rem', fontWeight: '700', color: '#991b1b', marginBottom: '6px' }}>
                Required Corrections for Category Acceptance:
              </div>
              <ul style={{ color: '#b91c1c', margin: '0 0 0 18px', fontSize: '0.875rem' }}>
                {missingItems.map((item, idx) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* STEP 1: ADAPTIVE FORM (VISIBLE BEFORE SUBMISSION) */}
      {!submittedData ? (
        <div className="card" style={{ padding: '32px' }}>
          <form onSubmit={handleSubmit}>
            <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '18px', marginBottom: '22px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f2942', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Building2 size={20} color="#1e40af" /> Step 1: Banking Institution &amp; Incident Category
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
                Fields dynamically adapt based on selected complaint type to ensure only relevant information is requested.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              {/* Financial Institution */}
              <div className="form-group">
                <label className="form-label">{t('bank_label')}</label>
                <select 
                  className="form-select" 
                  value={companyId} 
                  onChange={(e) => setCompanyId(e.target.value)}
                  required
                >
                  {companies.map(c => (
                    <option key={c.company_id} value={c.company_id}>{c.company_name}</option>
                  ))}
                </select>
              </div>

              {/* Service Type Selection */}
              <div className="form-group">
                <label className="form-label">{t('service_category_label')}</label>
                <select 
                  className="form-select" 
                  value={serviceType} 
                  onChange={(e) => setServiceType(e.target.value)}
                  required
                  style={{ fontWeight: '600', color: '#1e3a8a' }}
                >
                  {Object.keys(SERVICE_CONFIGS).map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* ADAPTIVE INCIDENT DETAILS SECTION */}
            <div style={{ 
              background: '#f8fafc', 
              padding: '20px', 
              borderRadius: '8px', 
              border: '1px solid #e2e8f0', 
              margin: '18px 0 24px 0' 
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: '700', color: '#334155', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Incident Parameters ({activeConfig.categoryGroup})
                </span>
                <span className="badge badge-blue">
                  {activeConfig.needsAmount ? "Financial Dispute" : "Service / Administrative Request"}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                {/* Transaction / Incident Date */}
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Incident / Transaction Date *</label>
                  <input 
                    type="date" 
                    className="form-input" 
                    value={transactionDate} 
                    onChange={(e) => setTransactionDate(e.target.value)}
                    required
                  />
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                    Cannot be futuristic; within 3 years limitation period.
                  </div>
                </div>

                {/* Amount (Conditional) */}
                {activeConfig.needsAmount && (
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">{activeConfig.amountLabel}</label>
                    <input 
                      type="number" 
                      step="0.01" 
                      placeholder="e.g. 4500.00" 
                      className="form-input" 
                      value={amount} 
                      onChange={(e) => setAmount(e.target.value)}
                      required={activeConfig.needsAmount}
                    />
                  </div>
                )}

                {/* Card Last 4 (Conditional) */}
                {activeConfig.needsCard4 && (
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">{activeConfig.card4Label}</label>
                    <input 
                      type="text" 
                      maxLength={4}
                      placeholder={activeConfig.card4Placeholder} 
                      className="form-input" 
                      value={cardLast4} 
                      onChange={(e) => setCardLast4(e.target.value)}
                      required={activeConfig.needsCard4}
                    />
                    <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                      Never share your full 16-digit card number or CVV.
                    </div>
                  </div>
                )}

                {/* Reference ID / UTR (Conditional) */}
                {activeConfig.needsRef && (
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">{activeConfig.refLabel}</label>
                    <input 
                      type="text" 
                      placeholder={activeConfig.refPlaceholder} 
                      className="form-input" 
                      value={referenceId} 
                      onChange={(e) => setReferenceId(e.target.value)}
                      required={activeConfig.needsRef}
                    />
                  </div>
                )}

                {/* Account Number / User ID (Conditional) */}
                {activeConfig.needsAccountNo && (
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">{activeConfig.accountNoLabel}</label>
                    <input 
                      type="text" 
                      placeholder={activeConfig.accountNoPlaceholder} 
                      className="form-input" 
                      value={accountNo} 
                      onChange={(e) => setAccountNo(e.target.value)}
                      required={activeConfig.needsAccountNo}
                    />
                  </div>
                )}

                {/* Home Branch / City */}
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <label className="form-label">Home Branch / Operating City</label>
                  <input 
                    type="text" 
                    placeholder="e.g. Mumbai Nariman Point or Andheri West" 
                    className="form-input" 
                    value={branch} 
                    onChange={(e) => setBranch(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* GRIEVANCE NARRATIVE & MULTILINGUAL INPUT */}
            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label className="form-label" style={{ marginBottom: 0 }}>
                  {t('narrative_label')}
                </label>
                <span style={{ fontSize: '0.8rem', color: '#2563eb', fontWeight: '600' }}>
                  {t('narrative_sub')}
                </span>
              </div>
              <textarea 
                rows="4" 
                className="form-textarea" 
                placeholder={lang === 'hi' ? t('narrative_placeholder') : activeConfig.descriptionHint}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                style={{ fontSize: '0.925rem', lineHeight: '1.55' }}
              ></textarea>
              <div style={{ display: 'flex', gap: '8px', marginTop: '6px', flexWrap: 'wrap', fontSize: '0.78rem', color: '#64748b' }}>
                <span>Example Hinglish: <em>"Mere account se 4500 rs kat gaye lekin samne wale ko receive nahi hue."</em></span>
              </div>
            </div>

            {/* ADAPTIVE PROOF FILE UPLOAD */}
            <div className="form-group" style={{ 
              background: activeConfig.needsProof ? '#f0f9ff' : '#f8fafc', 
              padding: '18px', 
              borderRadius: '8px', 
              border: activeConfig.needsProof ? '1px dashed #0284c7' : '1px dashed #cbd5e1' 
            }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: activeConfig.needsProof ? '#0369a1' : '#334155' }}>
                <Upload size={18} color={activeConfig.needsProof ? "#0284c7" : "#64748b"} /> 
                {activeConfig.proofLabel}
              </label>
              <p style={{ fontSize: '0.825rem', color: '#64748b', marginBottom: '12px' }}>
                {activeConfig.proofHint}
              </p>
              <input 
                type="file" 
                onChange={handleFileChange}
                accept=".pdf,.jpg,.jpeg,.png,.bmp,.txt"
                required={activeConfig.needsProof}
              />
              
              {/* Real-time validation feedback */}
              {docValidating && (
                <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px', color: '#0284c7', fontSize: '0.82rem', fontWeight: '600' }}>
                  <div style={{ width: '14px', height: '14px', border: '2px solid #0284c7', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.7s linear infinite' }} />
                  Verifying document against complaint category...
                </div>
              )}

              {!docValidating && docValid === true && proofFile && (
                <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '8px', color: '#16a34a', fontSize: '0.82rem', fontWeight: '700', background: '#f0fdf4', padding: '8px 12px', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                  <CheckCircle size={15} /> Document verified — content appears relevant to the selected complaint category.
                </div>
              )}

              {!docValidating && docWarnings.length > 0 && (
                <div style={{ marginTop: '10px', background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '6px', padding: '10px 14px' }}>
                  <div style={{ color: '#991b1b', fontWeight: '700', fontSize: '0.85rem', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AlertTriangle size={15} /> Invalid Document Detected — Please Upload Valid Proof
                  </div>
                  {docWarnings.map((w, i) => (
                    <div key={i} style={{ color: '#b91c1c', fontSize: '0.8rem', marginBottom: '4px' }}>• {w}</div>
                  ))}
                  <div style={{ marginTop: '6px', fontSize: '0.75rem', color: '#7f1d1d', fontStyle: 'italic', fontWeight: '500' }}>
                    Non-banking files (e.g. college lab manuals, assignments, personal notes) or documents with conflicting transaction numbers will be rejected by the validation engine.
                  </div>
                </div>
              )}

            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={loading}
              style={{ width: '100%', padding: '15px', fontSize: '1rem', fontWeight: '700', marginTop: '12px', letterSpacing: '0.01em' }}
            >
              {loading ? t('evaluating_btn') : t('submit_btn')}
            </button>
          </form>
        </div>
      ) : (
        /* STEP 2: TIER-1 SETTLEMENT DESK GUIDANCE & CUSTOMER CONFIRMATION SCREEN */
        <div>
          {/* SUCCESS HEADER */}
          <div className="card" style={{ borderLeft: '6px solid var(--accent)', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '15px' }}>
              <div>
                <span className="badge badge-blue" style={{ fontSize: '0.85rem' }}>
                  Statutory Tracking Token: {submittedData.token}
                </span>
                <h2 style={{ fontSize: '1.5rem', fontWeight: '800', marginTop: '10px', color: '#0f2942' }}>
                  Grievance Formally Registered
                </h2>
                <p style={{ color: '#475569', fontSize: '0.925rem', marginTop: '4px' }}>
                  Assigned Department: <strong>{submittedData.department}</strong> | Priority: <strong>{submittedData.priority}</strong>
                </p>
                {submittedData.sub_category && (
                  <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '2px' }}>
                    Sub-Category: <strong>{submittedData.sub_category}</strong> ({Math.round((submittedData.sub_category_confidence || 0.85) * 100)}% Match)
                  </p>
                )}
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600' }}>Quality Validity Score</div>
                <div style={{ fontSize: '1.75rem', fontWeight: '800', color: '#16a34a' }}>
                  {submittedData.validity_score} / 100
                </div>
                <span className="badge badge-green">Grievance Verified &amp; Actionable</span>
              </div>
            </div>

            {/* OCR & DUPLICATE CHECK BADGES */}
            <div style={{ display: 'flex', gap: '10px', marginTop: '16px', flexWrap: 'wrap' }}>
              {submittedData.ocr_verification?.has_document ? (
                <span className="badge badge-purple">
                  Document Audit: {submittedData.ocr_verification.verification_badge} {submittedData.ocr_verification.is_simulated ? '(SIMULATED)' : ''}
                </span>
              ) : (
                <span className="badge badge-gray">Proof Document: Not Required for Category</span>
              )}
              {submittedData.duplicate_check?.is_duplicate ? (
                <span className="badge badge-red">
                  Duplicate Reference Flagged ({submittedData.duplicate_check.matched_token})
                </span>
              ) : (
                <span className="badge badge-gray">
                  Unique Transaction Reference Confirmed
                </span>
              )}
            </div>
          </div>

          {/* TIER-1 SETTLEMENT DESK ADVISORY CARD */}
          <div className="card" style={{ border: '2px solid #175cd3', background: '#f8fafc', padding: '28px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', color: '#0a2540', marginBottom: '16px' }}>
              <Landmark size={26} color="#175cd3" />
              <h3 style={{ fontSize: '1.3rem', fontWeight: '800' }}>
                Grievance Redressal Guidance &amp; Action Steps
              </h3>
              <span className="badge badge-blue" style={{ marginLeft: 'auto' }}>
                Match Score: {(submittedData.bot_assessment?.bot_confidence * 100).toFixed(0)}%
              </span>
            </div>

            {/* Notice on desk advisory */}
            <div style={{ background: '#eff8ff', padding: '12px 16px', borderRadius: '8px', fontSize: '0.85rem', color: '#175cd3', marginBottom: '18px', border: '1px solid #b2ddff' }}>
              <strong>Grievance Redressal Notice:</strong> The guidance below outlines actionable steps, chargeback protocol, and preliminary remediation advice under RBI Banking Ombudsman regulations. Follow the steps to expedite your resolution.
            </div>

            <div style={{ background: '#ffffff', padding: '22px', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
              <h4 style={{ color: '#0f2942', fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>
                {submittedData.bot_assessment?.title}
              </h4>
              <p style={{ color: '#475569', fontSize: '0.925rem', marginBottom: '14px', lineHeight: '1.5' }}>
                {submittedData.bot_assessment?.summary}
              </p>

              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #175cd3' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                  <strong style={{ fontSize: '0.9rem', color: '#0f2942' }}>Resolution Steps &amp; Guidance:</strong>
                  <span className="badge badge-blue">
                    Assigned Desk: {submittedData.bot_assessment?.bot_name || 'Grievance Desk'} ({submittedData.bot_assessment?.bot_role || 'Specialist'})
                  </span>
                </div>
                <pre style={{ whiteSpace: 'pre-line', fontFamily: 'inherit', fontSize: '0.9rem', color: '#334155', marginTop: '6px', lineHeight: '1.65' }}>
                  {submittedData.bot_assessment?.guidance_steps}
                </pre>
              </div>

              {/* SLA Target & Proof Document */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginTop: '16px' }}>
                <div style={{ background: '#eff8ff', padding: '12px 16px', borderRadius: '8px', border: '1px solid #b2ddff', fontSize: '0.85rem' }}>
                  <div style={{ color: '#175cd3', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Clock size={16} /> Target Resolution SLA Window
                  </div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '800', color: '#0a2540', marginTop: '4px' }}>
                    {submittedData.bot_assessment?.sla_target_display || 'Within 24 Hours'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                    Automatic regulatory escalation if breached
                  </div>
                </div>

                {submittedData.bot_assessment?.proof_file && (
                  <div style={{ background: '#ecfdf3', padding: '12px 16px', borderRadius: '8px', border: '1px solid #a6f4c5', fontSize: '0.85rem' }}>
                    <div style={{ color: '#027a48', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <FileCheck size={16} /> Official Remediation Advice &amp; Proof
                    </div>
                    <a 
                      href={`http://localhost:8000/uploads/${submittedData.bot_assessment.proof_file}`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-outline"
                      style={{ marginTop: '6px', padding: '6px 12px', fontSize: '0.8rem', color: '#027a48', borderColor: '#a6f4c5', background: 'white' }}
                    >
                      Download Remediation Advice
                    </a>
                  </div>
                )}
              </div>

              <div style={{ marginTop: '14px', fontSize: '0.825rem', color: '#64748b' }}>
                <strong>Statutory Reference:</strong> {submittedData.bot_assessment?.regulatory_reference}
              </div>
            </div>

            {/* CUSTOMER DECISION BUTTONS */}
            {!decisionFinished ? (
              <div style={{ marginTop: '26px' }}>
                <p style={{ fontWeight: '700', color: '#0f2942', marginBottom: '14px', fontSize: '1rem' }}>
                  Customer Resolution Confirmation:
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                  <button 
                    onClick={() => handleCustomerDecision('SOLVED')}
                    disabled={decisionLoading}
                    className="btn btn-success"
                    style={{ padding: '16px', fontSize: '0.95rem', fontWeight: '700' }}
                  >
                    <CheckCircle size={20} />
                    This Solved My Issue (Close Grievance)
                  </button>

                  <button 
                    onClick={() => handleCustomerDecision('ESCALATE')}
                    disabled={decisionLoading}
                    className="btn btn-danger"
                    style={{ padding: '16px', fontSize: '0.95rem', fontWeight: '700' }}
                  >
                    <AlertTriangle size={20} />
                    Escalate to Grievance Redressal Officer
                  </button>
                </div>
              </div>
            ) : (
              /* POST-DECISION CONFIRMATION */
              <div style={{ marginTop: '24px', padding: '20px', borderRadius: '10px', background: decisionFinished.decision === 'SOLVED' ? '#ecfdf3' : '#fffaeb', border: '1px solid ' + (decisionFinished.decision === 'SOLVED' ? '#a6f4c5' : '#fedf89') }}>
                <h4 style={{ color: decisionFinished.decision === 'SOLVED' ? '#027a48' : '#b54708', fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px' }}>
                  {decisionFinished.decision === 'SOLVED' ? 'Grievance Closed via Electronic Redressal' : 'Escalated to Senior Grievance Redressal Officer'}
                </h4>
                <p style={{ color: '#475569', fontSize: '0.925rem', lineHeight: '1.5' }}>
                  {decisionFinished.message}
                </p>
                {decisionFinished.officer && (
                  <p style={{ marginTop: '8px', fontSize: '0.9rem', color: '#0f2942' }}>
                    Assigned Officer: <strong>{decisionFinished.officer}</strong>
                  </p>
                )}

                <div style={{ marginTop: '18px', display: 'flex', gap: '12px' }}>
                  <button 
                    onClick={() => navigate(`/track?token=${submittedData.token}`)}
                    className="btn btn-primary"
                  >
                    Track Progress &amp; View Audit Log <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
