import React, { createContext, useContext, useState, useEffect } from 'react';

export const translations = {
  en: {
    // ─── Nav & Common ────────────────────────────────────────────────────────
    app_title: "GrievanceIQ",
    portal_admin: "ADMIN PORTAL",
    portal_officer: "OFFICER PORTAL",
    portal_customer: "GRIEVANCE PORTAL",
    nav_submit: "Submit Complaint",
    nav_track: "Track Complaint",
    nav_history: "My History",
    nav_officer_workspace: "Officer Workspace",
    nav_admin_console: "Admin Console",
    nav_sign_in: "Portal Sign In",
    nav_sign_out: "Sign Out",
    refresh: "Refresh",
    footer_text: "GrievanceIQ © 2026 • Banking Grievance Redressal Management System • CFPB Consumer Protection & RBI Ombudsman Dataset",

    // ─── Language Picker ─────────────────────────────────────────────────────
    lang_label: "Language / भाषा",
    lang_en: "English",
    lang_hi: "हिंदी (Hindi)",

    // ─── Auth / Login & Register ─────────────────────────────────────────────
    login_portal_title: "Banking Redressal Portal",
    login_rbi_badge: "RBI Ombudsman Framework Compliant",
    login_hero_line1: "Your Banking Grievances,",
    login_hero_line2: "Resolved Digitally.",
    login_hero_desc: "Submit, track, and resolve banking complaints with our intelligent grievance management system. Fast resolutions backed by statutory consumer protection standards.",
    login_feat_1: "Secure end-to-end complaint processing",
    login_feat_2: "Priority-based resolution within 24–72 hours",
    login_feat_3: "Digital proof of resolution generated automatically",
    login_feat_4: "Complaints in English, Hindi & Hinglish accepted",
    login_rbi_scheme: "Protected under Reserve Bank of India Integrated Ombudsman Scheme, 2021",
    login_cust_tab: "👤 Customer Portal",
    login_staff_tab: "🏦 Staff Login",
    login_welcome_back: "Welcome back",
    login_create_acc: "Create your account",
    login_staff_title: "Staff & Admin Access",
    login_cust_subtitle: "Sign in to your GrievanceIQ account.",
    login_register_subtitle: "Register to file and track your banking complaints.",
    login_staff_subtitle: "Authorized access for bank officers and administrators.",
    login_tab_signin: "Sign In",
    login_tab_signup: "Create Account",
    login_email_label: "Registered Email",
    login_official_email: "Official Email Address",
    login_password_label: "Password",
    login_fullname_label: "Full Name",
    login_confirm_password: "Confirm Password",
    login_btn_signin: "Sign In",
    login_btn_staff_signin: "Sign In to Staff Portal",
    login_btn_create: "Create Customer Account",
    login_signing_in: "Signing in...",
    login_verifying: "Verifying identity...",
    login_creating: "Creating account...",
    login_no_acc: "Don't have an account?",
    login_register_here: "Register here",
    login_already_acc: "Already have an account?",
    login_signin_here: "Sign in here",
    login_staff_disclaimer: "This portal is restricted to authorized banking personnel. Unauthorized access is a punishable offence under the IT Act 2000.",

    // ─── Customer Submit Page ────────────────────────────────────────────────
    submit_title: "Statutory Banking Grievance Registration",
    submit_subtitle: "Register your formal dispute with designated Banking Ombudsmen & Nodal Officers under RBI Consumer Protection Framework.",
    service_category_label: "Dispute Category / Nature of Grievance *",
    bank_label: "Bank / Financial Institution *",
    date_label: "Date of Incident / Transaction *",
    branch_label: "Branch / City (Optional)",
    amount_label: "Disputed Transaction Amount (₹) *",
    ref_label: "Transaction Reference / UTR Number *",
    card_last4_label: "Last 4 Digits of Card (Debit/Credit)",
    account_no_label: "Bank Account Number / Customer ID",
    narrative_label: "Detailed Grievance Narrative * (Min 10-15 words)",
    narrative_sub: "English / हिंदी / Hinglish Supported",
    narrative_placeholder: "Describe the exact incident in detail...",
    submit_btn: "Register Formal Grievance & Initiate Settlement Review",
    evaluating_btn: "Evaluating Complaint Validity & Triaging Case...",

    // Evidence upload
    proof_title: "Payment Confirmation Receipt / Bank Statement Scan * (Mandatory)",
    proof_hint: "Screenshot of failed UPI payment, debit SMS confirmation, or passbook entry (JPG, PNG, PDF).",
    doc_verifying: "Verifying document against complaint category...",
    doc_verified: "Document verified — content appears relevant to the selected complaint category.",
    doc_invalid_title: "Invalid Document Detected — Please Upload Valid Proof",

    // ─── Tracking Page ───────────────────────────────────────────────────────
    track_title: "Official Grievance Tracking & Verification",
    track_subtitle: "Query live audit trails, resolution documents, and communications directly from bank systems.",
    token_placeholder: "Enter Grievance Reference Token (e.g. GRV-2026-00312)",
    track_btn: "Track Grievance",
    status_label: "Complaint Status",
    sla_deadline: "SLA Resolution Deadline",
    assigned_desk: "Designated Settlement Desk",

    // ─── Customer History Page ───────────────────────────────────────────────
    history_title: "My Lodged Grievance History",
    history_subtitle: "View the status, officer notes, resolution letters, and decisions for all your complaints.",
    total_complaints: "Total Lodged",
    active_cases: "Active Cases",
    resolved_cases: "Resolved",
    action_needed: "Action Needed",
    reopen_btn: "Reopen Case",
    accept_btn: "Accept Resolution",
    dispute_btn: "Dispute Resolution",

    // ─── Officer / Employee Workspace ────────────────────────────────────────
    officer_title: "GrievanceIQ — Officer Workspace",
    officer_badge: "Banking Officer",
    officer_stat_total: "Total Cases",
    officer_stat_resolved: "Resolved",
    officer_stat_pending: "Pending",
    officer_stat_high_priority: "High Priority",
    officer_stat_sla_breached: "SLA Breached",
    officer_stat_rate: "Resolution Rate",
    officer_queue_title: "Case Queue",
    officer_search_placeholder: "Search by token, customer, type...",
    officer_filter_all_status: "All Status",
    officer_filter_all_priority: "All Priority",
    officer_no_cases: "No complaints match your filters.",
    officer_select_case_prompt: "Select a case from the queue on the left to review details, inspect evidence, add notes, or propose a resolution.",
    officer_tab_details: "Case Details",
    officer_tab_evidence: "AI Evidence Scrutiny",
    officer_tab_notes: "Investigation Notes",
    officer_tab_resolve: "Submit Resolution",
    officer_tab_messages: "Customer Messages",
    officer_desc_label: "Customer Statement",
    officer_details_label: "Case Metadata",
    officer_txn_amount: "Disputed Amount",
    officer_txn_date: "Incident Date",
    officer_ref_id: "Reference / UTR",
    officer_customer: "Complainant",
    officer_bank: "Bank / Institution",
    officer_dept: "Assigned Department",
    officer_validity_score: "Validity Score",
    officer_sla_deadline: "SLA Deadline",
    officer_attached_doc: "Attached Evidence Document",
    officer_view_doc: "View Document",
    officer_btn_in_progress: "Mark In-Progress",
    officer_btn_escalate: "Escalate to Nodal / Ombudsman",
    officer_btn_close: "Close Case",
    officer_btn_reopen: "Reopen Case",
    officer_ai_run_analysis: "Run AI Document Verification",
    officer_ai_confidence: "AI Confidence Score",
    officer_ai_recommendation: "AI Recommendation",
    officer_ai_breakdown: "Confidence Breakdown",
    officer_ai_accept: "Accept Evidence & Verify",
    officer_ai_reject: "Reject Document as Inadequate",
    officer_res_type: "Resolution Type *",
    officer_res_details: "Resolution Details & Justification *",
    officer_res_ref: "Payment / Refund UTR Reference",
    officer_res_amount: "Refund / Settled Amount (₹)",
    officer_res_letter: "Upload Resolution Letter / Payment Slip (PDF/JPG)",
    officer_res_submit: "Finalize & Issue Resolution",
    officer_notes_add: "Add Investigation Note",
    officer_notes_save: "Save Note",
    officer_msg_placeholder: "Type message to customer...",
    officer_msg_send: "Send Message",

    // ─── Admin Dashboard / Command Console ───────────────────────────────────
    admin_title: "Banking Grievance Command & Control Console",
    admin_subtitle: "Macro analytics, what-if resource simulation, institution ranking, and ombudsman supervision.",
    admin_tab_queue: "Grievance Queue",
    admin_tab_analytics: "Macro Analytics",
    admin_tab_whatif: "What-If Simulator",
    admin_tab_intelligence: "Predictive Intelligence",
    admin_tab_kb: "Knowledge Base / Playbook",
    admin_tab_audit: "Audit Logs",
    admin_kpi_total: "Total Complaints",
    admin_kpi_pending: "Pending Cases",
    admin_kpi_resolved: "Resolved",
    admin_kpi_rate: "Resolution Rate",
    admin_kpi_tat: "Average TAT",
    admin_kpi_sla_compliance: "SLA Compliance",
    admin_filter_bank: "All Banks",
    admin_filter_dept: "All Departments",
    admin_filter_priority: "All Priorities",
    admin_filter_status: "All Statuses",
    admin_search_placeholder: "Search token, customer, bank, keyword...",
    admin_col_token: "Token",
    admin_col_date: "Lodged Date",
    admin_col_customer: "Customer",
    admin_col_bank: "Bank",
    admin_col_dept: "Department",
    admin_col_amount: "Amount",
    admin_col_priority: "Priority",
    admin_col_validity: "Validity",
    admin_col_status: "Status",
    admin_col_sla: "SLA",
    admin_col_actions: "Actions",
    admin_btn_view: "Review Case",
    admin_btn_export: "Export CSV",

    // What-If Simulator
    admin_sim_heading: "Bank-Wise & Department-Wise What-If Resource Simulation",
    admin_sim_sub: "Estimate how changes in officer staffing and complaint volumes impact pending caseloads, resolution turnaround time (TAT), and SLA breach risk.",
    admin_sim_bank_select: "Select Bank / Institution",
    admin_sim_dept_select: "Select Department",
    admin_sim_workers: "Proposed Officer Count",
    admin_sim_vol_change: "Projected Complaint Volume Shift (%)",
    admin_sim_run: "Execute Simulation",
    admin_sim_reset: "Reset to Defaults",
    admin_sim_current_workers: "Current Officers",
    admin_sim_current_pending: "Current Pending",
    admin_sim_current_tat: "Current Avg TAT",
    admin_sim_proj_tat: "Projected TAT",
    admin_sim_tat_change: "TAT Improvement",
    admin_sim_proj_pending: "Projected Pending",
    admin_sim_sla_score: "SLA Pressure Score",
    admin_sim_breach_risk: "Breach Risk Probability",
    admin_sim_disclaimer: "Scenario Estimate — Mathematical projection derived from operational data. Not a guaranteed outcome.",

    // ─── Statuses ────────────────────────────────────────────────────────────
    status_open: "Open",
    status_in_progress: "In Progress",
    status_escalated: "Escalated",
    status_resolution_proposed: "Resolution Proposed",
    status_resolved: "Resolved",
    status_closed: "Closed",
    status_reopened: "Reopened",

    // ─── Priorities ──────────────────────────────────────────────────────────
    priority_High: "High Priority",
    priority_Medium: "Medium Priority",
    priority_Low: "Low Priority",

    // ─── Departments ─────────────────────────────────────────────────────────
    dept_upi: "Digital & UPI Banking",
    dept_loans: "Loans & Advances",
    dept_cards: "Cards & ATM Services",
    dept_operations: "Account & Branch Operations",
    dept_fraud: "Fraud & Risk Management"
  },
  hi: {
    // ─── Nav & Common ────────────────────────────────────────────────────────
    app_title: "शिकायतIQ (GrievanceIQ)",
    portal_admin: "व्यवस्थापक पोर्टल (ADMIN)",
    portal_officer: "अधिकारी पोर्टल (OFFICER)",
    portal_customer: "शिकायत निवारण पोर्टल",
    nav_submit: "शिकायत दर्ज करें",
    nav_track: "शिकायत ट्रैक करें",
    nav_history: "शिकायत इतिहास",
    nav_officer_workspace: "अधिकारी कार्यक्षेत्र",
    nav_admin_console: "व्यवस्थापक कंसोल",
    nav_sign_in: "पोर्टल लॉगिन",
    nav_sign_out: "लॉग आउट",
    refresh: "ताज़ा करें",
    footer_text: "शिकायतIQ © 2026 • बैंकिंग शिकायत निवारण प्रबंधन प्रणाली • आरबीआई एवं उपभोक्ता संरक्षण रूपरेखा",

    // ─── Language Picker ─────────────────────────────────────────────────────
    lang_label: "Language / भाषा",
    lang_en: "English",
    lang_hi: "हिंदी (Hindi)",

    // ─── Auth / Login & Register ─────────────────────────────────────────────
    login_portal_title: "बैंकिंग शिकायत निवारण पोर्टल",
    login_rbi_badge: "आरबीआई लोकपाल रूपरेखा अनुपालक",
    login_hero_line1: "आपकी बैंकिंग शिकायतें,",
    login_hero_line2: "डिजिटल त्वरित समाधान।",
    login_hero_desc: "हमारी बुद्धिमान शिकायत प्रबंधन प्रणाली से बैंकिंग शिकायतों को दर्ज, ट्रैक और हल करें। वैधानिक उपभोक्ता संरक्षण नियमों के तहत त्वरित एवं पारदर्शी समाधान।",
    login_feat_1: "सुरक्षित एंड-टू-एंड शिकायत प्रसंस्करण",
    login_feat_2: "24–72 घंटों में प्राथमिकता-आधारित समाधान",
    login_feat_3: "समाधान का डिजिटल प्रमाण पत्र स्वतः उत्पन्न",
    login_feat_4: "अंग्रेजी, हिंदी एवं हिंग्लिश में शिकायतें मान्य",
    login_rbi_scheme: "भारतीय रिजर्व बैंक एकीकृत लोकपाल योजना, 2021 के अंतर्गत संरक्षित",
    login_cust_tab: "👤 ग्राहक पोर्टल",
    login_staff_tab: "🏦 बैंक स्टाफ एवं व्यवस्थापक",
    login_welcome_back: "वापसी पर स्वागत है",
    login_create_acc: "नया खाता बनाएं",
    login_staff_title: "बैंक कर्मचारी एवं व्यवस्थापक लॉगिन",
    login_cust_subtitle: "अपने शिकायतIQ खाते में लॉगिन करें।",
    login_register_subtitle: "अपनी बैंकिंग शिकायतों को दर्ज और ट्रैक करने हेतु पंजीकरण करें।",
    login_staff_subtitle: "अधिकृत बैंक अधिकारियों और व्यवस्थापकों के लिए सुरक्षित पहुंच।",
    login_tab_signin: "लॉगिन करें",
    login_tab_signup: "खाता बनाएं",
    login_email_label: "पंजीकृत ईमेल पता",
    login_official_email: "कार्यालयी ईमेल पता",
    login_password_label: "पासवर्ड",
    login_fullname_label: "पूरा नाम",
    login_confirm_password: "पासवर्ड की पुष्टि करें",
    login_btn_signin: "लॉगिन करें",
    login_btn_staff_signin: "स्टाफ पोर्टल में लॉगिन करें",
    login_btn_create: "ग्राहक खाता बनाएं",
    login_signing_in: "साइन इन हो रहा है...",
    login_verifying: "पहचान सत्यापित की जा रही है...",
    login_creating: "खाता बनाया जा रहा है...",
    login_no_acc: "क्या आपका खाता नहीं है?",
    login_register_here: "यहाँ पंजीकरण करें",
    login_already_acc: "क्या आपके पास पहले से खाता है?",
    login_signin_here: "यहाँ लॉगिन करें",
    login_staff_disclaimer: "यह पोर्टल केवल अधिकृत बैंकिंग कर्मियों के लिए सीमित है। अनधिकृत प्रवेश आईटी अधिनियम 2000 के तहत दंडनीय अपराध है।",

    // ─── Customer Submit Page ────────────────────────────────────────────────
    submit_title: "वैधानिक बैंकिंग शिकायत पंजीकरण",
    submit_subtitle: "आरबीआई उपभोक्ता संरक्षण नियमों के तहत नामित बैंकिंग लोकपाल और नोडल अधिकारियों के पास शिकायत दर्ज करें।",
    service_category_label: "विवाद श्रेणी / शिकायत का प्रकार *",
    bank_label: "बैंक / वित्तीय संस्थान का चयन करें *",
    date_label: "लेनदेन / घटना की तिथि *",
    branch_label: "शाखा / शहर (वैकल्पिक)",
    amount_label: "विवादित लेनदेन राशि (₹) *",
    ref_label: "लेनदेन संदर्भ संख्या / यूटीआर (UTR) *",
    card_last4_label: "कार्ड के अंतिम 4 अंक (डेबिट/क्रेडिट)",
    account_no_label: "बैंक खाता संख्या / ग्राहक आईडी",
    narrative_label: "शिकायत का विस्तृत विवरण * (कम से कम 10-15 शब्द)",
    narrative_sub: "अंग्रेजी / हिंदी / हिंग्लिश समर्थित",
    narrative_placeholder: "कृपया जो कुछ हुआ उसका स्पष्ट विवरण यहाँ लिखें...",
    submit_btn: "औपचारिक शिकायत दर्ज करें और समीक्षा शुरू करें",
    evaluating_btn: "शिकायत की वैधता का मूल्यांकन और वर्गीकरण किया जा रहा है...",

    // Evidence upload
    proof_title: "भुगतान पुष्टि रसीद / बैंक स्टेटमेंट कॉपी * (अनिवार्य)",
    proof_hint: "असफल भुगतान का स्क्रीनशॉट, डेबिट एसएमएस या पासबुक प्रविष्टि (JPG, PNG, PDF)।",
    doc_verifying: "दस्तावेज़ की जाँच की जा रही है...",
    doc_verified: "दस्तावेज़ सत्यापित — सामग्री चयनित शिकायत श्रेणी के लिए प्रासंगिक है।",
    doc_invalid_title: "अमान्य दस्तावेज़ पहचाना गया — कृपया सही रसीद अपलोड करें",

    // ─── Tracking Page ───────────────────────────────────────────────────────
    track_title: "आधिकारिक शिकायत ट्रैकिंग एवं सत्यापन",
    track_subtitle: "बैंक प्रणालियों से सीधे लाइव स्थिति, जांच रिपोर्ट और समाधान दस्तावेज़ देखें।",
    token_placeholder: "शिकायत टोकन दर्ज करें (उदा. GRV-2026-00312)",
    track_btn: "शिकायत ट्रैक करें",
    status_label: "शिकायत स्थिति",
    sla_deadline: "समाधान की अंतिम समय-सीमा",
    assigned_desk: "नामित समाधान डेस्क",

    // ─── Customer History Page ───────────────────────────────────────────────
    history_title: "मेरे द्वारा दर्ज शिकायतों का इतिहास",
    history_subtitle: "अपनी सभी शिकायतों की स्थिति, अधिकारी की टिप्पणी और समाधान पत्र देखें।",
    total_complaints: "कुल शिकायतें",
    active_cases: "प्रगति में",
    resolved_cases: "समाधानित",
    action_needed: "कार्रवाई आवश्यक",
    reopen_btn: "मामला पुनः खोलें",
    accept_btn: "समाधान स्वीकार करें",
    dispute_btn: "समाधान अस्वीकार / विवाद करें",

    // ─── Officer / Employee Workspace ────────────────────────────────────────
    officer_title: "शिकायतIQ — अधिकारी कार्यक्षेत्र",
    officer_badge: "बैंकिंग अधिकारी",
    officer_stat_total: "कुल मामले",
    officer_stat_resolved: "समाधानित",
    officer_stat_pending: "लंबित",
    officer_stat_high_priority: "अति प्राथमिकता",
    officer_stat_sla_breached: "समय-सीमा उल्लंघन",
    officer_stat_rate: "समाधान दर",
    officer_queue_title: "शिकायत कतार",
    officer_search_placeholder: "टोकन, ग्राहक या विवरण खोजें...",
    officer_filter_all_status: "सभी स्थितियाँ",
    officer_filter_all_priority: "सभी प्राथमिकताएं",
    officer_no_cases: "आपके फ़िल्टर से कोई शिकायत मेल नहीं खाती।",
    officer_select_case_prompt: "विवरण की समीक्षा करने, साक्ष्य जांचने, जांच नोट जोड़ने या समाधान प्रस्तावित करने के लिए बाईं ओर की कतार से एक केस चुनें।",
    officer_tab_details: "शिकायत विवरण",
    officer_tab_evidence: "एआई साक्ष्य सत्यापन",
    officer_tab_notes: "जांच नोट्स",
    officer_tab_resolve: "समाधान प्रस्तुत करें",
    officer_tab_messages: "ग्राहक संदेश",
    officer_desc_label: "शिकायतकर्ता का विवरण",
    officer_details_label: "केस मेटाडेटा",
    officer_txn_amount: "विवादित राशि",
    officer_txn_date: "घटना की तिथि",
    officer_ref_id: "संदर्भ संख्या / UTR",
    officer_customer: "शिकायतकर्ता",
    officer_bank: "बैंक / संस्थान",
    officer_dept: "आवंटित विभाग",
    officer_validity_score: "वैधता स्कोर",
    officer_sla_deadline: "समय-सीमा (SLA)",
    officer_attached_doc: "संलग्न साक्ष्य दस्तावेज़",
    officer_view_doc: "दस्तावेज़ देखें",
    officer_btn_in_progress: "प्रगति में चिह्नित करें",
    officer_btn_escalate: "नोडल / लोकपाल को अग्रेषित करें",
    officer_btn_close: "मामला बंद करें",
    officer_btn_reopen: "मामला पुनः खोलें",
    officer_ai_run_analysis: "एआई दस्तावेज़ सत्यापन चलाएं",
    officer_ai_confidence: "एआई विश्वसनीयता स्कोर",
    officer_ai_recommendation: "एआई अनुशंसा",
    officer_ai_breakdown: "विश्वसनीयता विवरण",
    officer_ai_accept: "साक्ष्य स्वीकार एवं सत्यापित करें",
    officer_ai_reject: "दस्तावेज़ अपर्याप्त मानकर अस्वीकार करें",
    officer_res_type: "समाधान का प्रकार *",
    officer_res_details: "समाधान विवरण एवं औचित्य *",
    officer_res_ref: "भुगतान / रिफंड यूटीआर संदर्भ",
    officer_res_amount: "स्वीकृत / रिफंड राशि (₹)",
    officer_res_letter: "समाधान पत्र / भुगतान रसीद अपलोड करें (PDF/JPG)",
    officer_res_submit: "समाधान को अंतिम रूप दें और जारी करें",
    officer_notes_add: "जांच नोट जोड़ें",
    officer_notes_save: "नोट सहेजें",
    officer_msg_placeholder: "ग्राहक को संदेश लिखें...",
    officer_msg_send: "संदेश भेजें",

    // ─── Admin Dashboard / Command Console ───────────────────────────────────
    admin_title: "बैंकिंग शिकायत नियंत्रण एवं प्रबंधन कंसोल",
    admin_subtitle: "व्यापक विश्लेषण, व्हाट-इफ संसाधन सिमुलेशन, बैंक रैंकिंग एवं लोकपाल पर्यवेक्षण।",
    admin_tab_queue: "शिकायत कतार",
    admin_tab_analytics: "व्यापक विश्लेषण",
    admin_tab_whatif: "व्हाट-इफ संसाधन सिमुलेटर",
    admin_tab_intelligence: "पूर्वानुमानित विश्लेषण",
    admin_tab_kb: "समाधान मार्गदर्शिका",
    admin_tab_audit: "सिस्टम ऑडिट लॉग्स",
    admin_kpi_total: "कुल शिकायतें",
    admin_kpi_pending: "लंबित मामले",
    admin_kpi_resolved: "समाधानित",
    admin_kpi_rate: "समाधान दर",
    admin_kpi_tat: "औसत समाधान समय",
    admin_kpi_sla_compliance: "SLA अनुपालन",
    admin_filter_bank: "सभी बैंक",
    admin_filter_dept: "सभी विभाग",
    admin_filter_priority: "सभी प्राथमिकताएं",
    admin_filter_status: "सभी स्थितियाँ",
    admin_search_placeholder: "टोकन, ग्राहक, बैंक या कीवर्ड खोजें...",
    admin_col_token: "टोकन",
    admin_col_date: "दर्ज तिथि",
    admin_col_customer: "ग्राहक",
    admin_col_bank: "बैंक",
    admin_col_dept: "विभाग",
    admin_col_amount: "राशि",
    admin_col_priority: "प्राथमिकता",
    admin_col_validity: "वैधता",
    admin_col_status: "स्थिति",
    admin_col_sla: "समय-सीमा",
    admin_col_actions: "कार्रवाई",
    admin_btn_view: "केस समीक्षा",
    admin_btn_export: "सीएसवी निर्यात",

    // What-If Simulator
    admin_sim_heading: "बैंक एवं विभाग-वार व्हाट-इफ संसाधन सिमुलेशन",
    admin_sim_sub: "अनुमान लगाएं कि अधिकारी कार्यबल और शिकायत मात्रा में परिवर्तन से लंबित मामलों, समाधान समय (TAT) और समय-सीमा उल्लंघन जोखिम पर क्या प्रभाव पड़ता है।",
    admin_sim_bank_select: "बैंक / वित्तीय संस्थान चुनें",
    admin_sim_dept_select: "विभाग का चयन करें",
    admin_sim_workers: "प्रस्तावित अधिकारी संख्या",
    admin_sim_vol_change: "अनुमानित शिकायत मात्रा परिवर्तन (%)",
    admin_sim_run: "सिमुलेशन चलाएं",
    admin_sim_reset: "रीसेट करें",
    admin_sim_current_workers: "वर्तमान अधिकारी",
    admin_sim_current_pending: "वर्तमान लंबित",
    admin_sim_current_tat: "वर्तमान औसत TAT",
    admin_sim_proj_tat: "अनुमानित TAT",
    admin_sim_tat_change: "TAT में सुधार",
    admin_sim_proj_pending: "अनुमानित लंबित",
    admin_sim_sla_score: "SLA दबाव स्कोर",
    admin_sim_breach_risk: "समय-सीमा उल्लंघन जोखिम",
    admin_sim_disclaimer: "परिदृश्य पूर्वानुमान — परिचालन डेटा पर आधारित गणितीय अनुमान। यह कोई गारंटीकृत परिणाम नहीं है।",

    // ─── Statuses ────────────────────────────────────────────────────────────
    status_open: "खुला (Open)",
    status_in_progress: "प्रगति में (In Progress)",
    status_escalated: "अग्रेषित (Escalated)",
    status_resolution_proposed: "समाधान प्रस्तावित",
    status_resolved: "समाधानित (Resolved)",
    status_closed: "बंद (Closed)",
    status_reopened: "पुनः खोला गया",

    // ─── Priorities ──────────────────────────────────────────────────────────
    priority_High: "अति प्राथमिकता (High)",
    priority_Medium: "मध्यम प्राथमिकता (Medium)",
    priority_Low: "सामान्य प्राथमिकता (Low)",

    // ─── Departments ─────────────────────────────────────────────────────────
    dept_upi: "डिजिटल एवं यूपीआई बैंकिंग",
    dept_loans: "ऋण एवं अग्रिम (Loans)",
    dept_cards: "कार्ड्स एवं एटीएम सेवाएं",
    dept_operations: "खाता एवं शाखा संचालन",
    dept_fraud: "धोखाधड़ी एवं जोखिम प्रबंधन"
  }
};

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [lang, setLang] = useState(() => {
    return localStorage.getItem('grievanceiq_lang') || 'en';
  });

  const changeLanguage = (newLang) => {
    setLang(newLang);
    localStorage.setItem('grievanceiq_lang', newLang);
  };

  const t = (key, fallback) => {
    if (translations[lang]?.[key]) return translations[lang][key];
    if (translations['en']?.[key]) return translations['en'][key];
    return fallback !== undefined ? fallback : key;
  };

  const tStatus = (status) => {
    const k = `status_${status}`;
    return translations[lang]?.[k] || translations['en']?.[k] || status;
  };

  const tPriority = (priority) => {
    const k = `priority_${priority}`;
    return translations[lang]?.[k] || translations['en']?.[k] || priority;
  };

  const tDept = (deptName) => {
    if (!deptName) return '';
    const norm = deptName.toLowerCase();
    if (norm.includes('upi') || norm.includes('digital')) return t('dept_upi');
    if (norm.includes('loan')) return t('dept_loans');
    if (norm.includes('card') || norm.includes('atm')) return t('dept_cards');
    if (norm.includes('operation') || norm.includes('branch')) return t('dept_operations');
    if (norm.includes('fraud') || norm.includes('risk')) return t('dept_fraud');
    return deptName;
  };

  return (
    <LanguageContext.Provider value={{ lang, changeLanguage, t, tStatus, tPriority, tDept }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
