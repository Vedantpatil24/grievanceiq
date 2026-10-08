-- =====================================================================
-- GrievanceIQ DBMS Analytics & Operational Queries
-- Standard SQL demonstrations for evaluators, vivas, and reports
-- =====================================================================

-- 1. Department Workload & Backlog Distribution
SELECT 
    d.name AS department_name,
    COUNT(c.id) AS total_complaints,
    SUM(CASE WHEN c.status = 'open' THEN 1 ELSE 0 END) AS open_count,
    SUM(CASE WHEN c.status = 'in_progress' THEN 1 ELSE 0 END) AS in_progress_count,
    SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN c.is_escalated = TRUE THEN 1 ELSE 0 END) AS escalated_breached_count
FROM departments d
LEFT JOIN complaints c ON d.id = c.department_id
GROUP BY d.id, d.name
ORDER BY total_complaints DESC;

-- 2. Bank Leaderboard & Resolution Efficiency Scoring
SELECT 
    comp.name AS bank_name,
    COUNT(c.id) AS total_complaints,
    SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN c.is_escalated = TRUE THEN 1 ELSE 0 END) AS breached_count,
    ROUND((SUM(CASE WHEN c.status = 'resolved' THEN 1.0 ELSE 0 END) / COUNT(c.id)) * 100, 2) AS resolution_rate_pct,
    ROUND(AVG(f.rating), 2) AS avg_csat_rating
FROM companies comp
JOIN complaints c ON comp.id = c.company_id
LEFT JOIN feedback f ON c.id = f.complaint_id
GROUP BY comp.id, comp.name
HAVING COUNT(c.id) > 100
ORDER BY resolution_rate_pct DESC, total_complaints DESC
LIMIT 10;

-- 3. Officer Fair Load Allocation & Resolution Audit
SELECT 
    w.employee_id,
    w.name AS officer_name,
    d.name AS department,
    COUNT(c.id) AS total_assigned,
    SUM(CASE WHEN c.status = 'resolved' THEN 1 ELSE 0 END) AS resolved,
    SUM(CASE WHEN c.is_escalated = TRUE THEN 1 ELSE 0 END) AS late_escalated
FROM workers w
JOIN departments d ON w.department_id = d.id
LEFT JOIN complaints c ON w.worker_id = c.assigned_worker_id
GROUP BY w.id, w.employee_id, w.name, d.name
ORDER BY total_assigned DESC;

-- 4. Urgent Regulatory Escalations (SLA Breaches)
SELECT 
    c.token,
    comp.name AS financial_institution,
    d.name AS department,
    c.priority,
    c.created_at,
    c.due_date,
    c.assigned_worker_id
FROM complaints c
JOIN companies comp ON c.company_id = comp.id
JOIN departments d ON c.department_id = d.id
WHERE c.is_escalated = TRUE AND c.status != 'resolved'
ORDER BY c.due_date ASC
LIMIT 20;

-- 5. AI Semantic Validity Audit Log
SELECT 
    c.token,
    c.validity_decision,
    c.validity_score,
    c.priority,
    c.service_type,
    c.rejection_reason
FROM complaints c
WHERE c.validity_decision IS NOT NULL
ORDER BY c.created_at DESC
LIMIT 25;
