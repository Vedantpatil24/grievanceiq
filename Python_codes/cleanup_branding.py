"""
Cleanup script: removes AI/Bot branding from bot_resolver.py
"""
with open('bot_resolver.py', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (
        'bot_resolver.py - Tier-1 AI GrievanceBot Engine with Dual Specialist Bots per Department',
        'bot_resolver.py - Automated Grievance Resolution Engine with Dual Settlement Desks per Department'
    ),
    (
        '1. 2 Specialized Bots per Banking Department (e.g. UPI Reversal Bot & POS Clearing Bot for Retail)',
        '1. 2 Specialized Desks per Banking Department (e.g. UPI Reversal Desk & POS Clearing Desk for Retail)'
    ),
    (
        'Generates an official Bot Resolution Proof Advice Document (Text/PDF-ready format).',
        'Generates an official Resolution Proof Advice Document (Text/PDF-ready format).'
    ),
    (
        'proof_bot_',
        'proof_desk_'
    ),
    (
        'Returns the two designated specialist bots for the department.',
        'Returns the two designated specialist desks for the department.'
    ),
    (
        'Tier-1 GrievanceBot analysis with 2 bots per department and SLA target calculation.',
        'Automated grievance assessment with 2 specialist desks per department and SLA target calculation.'
    ),
    (
        '# Resolve assigned bot from the 2 department bots',
        '# Resolve assigned desk from the 2 department desks'
    ),
    (
        '# Pick Primary Bot (Bot 0) for general/service or Secondary Bot (Bot 1) for fraud/penalties',
        '# Pick Primary Desk (Desk 0) for general/service or Secondary Desk (Desk 1) for fraud/penalties'
    ),
    (
        'Tier-1 AI specialist bot recommends human nodal escalation.',
        'Direct review by a senior Grievance Redressal Officer is recommended.'
    ),
    (
        '# 2. Return bot assessment',
        '# 2. Return desk assessment'
    ),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'  Replaced: {old[:60]}...')
    else:
        print(f'  NOT FOUND: {old[:60]}')

with open('bot_resolver.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
import re
remaining = re.findall(r'Tier-1 AI|GrievanceBot Engine', content)
print('Remaining AI/Bot violations:', remaining if remaining else 'NONE — clean!')
print('Done.')
