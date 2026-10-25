import React, { useState, useEffect } from 'react';
import { Bot, X, Send, Sparkles, HelpCircle, ShieldCheck, ChevronRight, MessageSquare } from 'lucide-react';

export default function NovaAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'nova',
      text: "Namaste! I am Nova, your GrievanceIQ Autonomous AI Sentinel. How can I assist you with filing, tracking, or resolving your banking dispute today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [floatingY, setFloatingY] = useState(0);

  // Subtle floating robot animation
  useEffect(() => {
    const interval = setInterval(() => {
      setFloatingY(prev => (prev === 0 ? -6 : 0));
    }, 1500);
    return () => clearInterval(interval);
  }, []);

  const handleSend = (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query) return;

    const newMsgs = [...messages, { sender: 'user', text: query }];
    setMessages(newMsgs);
    if (!textToSend) setInput('');
    setIsTyping(true);

    setTimeout(() => {
      let reply = "I am processing your query under RBI Consumer Protection & Grievance Guidelines.";
      const q = query.toLowerCase();

      if (q.includes('submit') || q.includes('file') || q.includes('lodge') || q.includes('how to')) {
        reply = "To submit a grievance: Click 'Submit Complaint' in the top bar. Pick your bank, choose the dispute category, input the transaction reference (UTR/Card last 4), and attach your payment receipt.";
      } else if (q.includes('track') || q.includes('status') || q.includes('where is my')) {
        reply = "To track an existing case: Go to 'Track Complaint' and enter your statutory token (e.g., GRV-2026-00262). You will see real-time investigation progress, SLA countdown, and resolution documents.";
      } else if (q.includes('time') || q.includes('how long') || q.includes('fast') || q.includes('sla')) {
        reply = "Standard valid cases are resolved by me (Nova-AI Sentinel) autonomously in under 30 seconds! Complex or contested cases routed to human officers are handled strictly within 24 to 72 hours under RBI TAT mandates.";
      } else if (q.includes('proof') || q.includes('document') || q.includes('screenshot')) {
        reply = "We accept PDF bank statements, transaction screenshots (JPG/PNG), or debit SMS logs. Our 5-Field OCR engine verifies the date, amount, and reference number automatically.";
      } else if (q.includes('who are you') || q.includes('name') || q.includes('nova')) {
        reply = "I am Nova, GrievanceIQ's Autonomous AI Sentinel. I inspect complaints, cross-verify transaction records, and generate statutory settlement memoranda under RBI guidelines.";
      } else {
        reply = "Understood. For immediate assistance with this grievance, you can also register the complaint on the portal or chat directly with your assigned officer via the Track Complaint portal.";
      }

      setMessages([...newMsgs, { sender: 'nova', text: reply }]);
      setIsTyping(false);
    }, 800);
  };

  return (
    <>
      {/* ── FLOATING NOVA ROBOT ICON ── */}
      <div
        onClick={() => setIsOpen(prev => !prev)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          cursor: 'pointer',
          transform: `translateY(${floatingY}px)`,
          transition: 'transform 1.2s ease-in-out',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}
      >
        {!isOpen && (
          <div style={{
            background: 'rgba(15, 23, 42, 0.92)',
            color: '#f8fafc',
            padding: '8px 14px',
            borderRadius: '20px',
            fontSize: '0.82rem',
            fontWeight: '600',
            boxShadow: '0 4px 14px rgba(0,0,0,0.2)',
            border: '1px solid rgba(255,255,255,0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Sparkles size={14} color="#38bdf8" />
            <span>Chat with <strong>Nova</strong></span>
          </div>
        )}

        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #1e40af, #3b82f6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 8px 24px rgba(37, 99, 235, 0.4)',
          border: '2px solid #93c5fd'
        }}>
          {isOpen ? <X size={26} color="#ffffff" /> : <Bot size={28} color="#ffffff" />}
        </div>
      </div>

      {/* ── NOVA CHAT WINDOW ── */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '92px',
          right: '24px',
          width: '380px',
          height: '520px',
          background: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 16px 40px rgba(0,0,0,0.22)',
          border: '1px solid #cbd5e1',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          fontFamily: "'Inter', system-ui, sans-serif"
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #091e33, #1e3a8a)',
            color: '#ffffff',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            borderBottom: '2px solid #38bdf8'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: '#1d4ed8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid #60a5fa'
              }}>
                <Bot size={20} color="#ffffff" />
              </div>
              <div>
                <div style={{ fontSize: '0.95rem', fontWeight: '800' }}>
                  Nova <span style={{ fontSize: '0.72rem', color: '#93c5fd', fontWeight: '500' }}>AI Sentinel</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#86efac', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e', display: 'inline-block' }}></span>
                  Autonomous Redressal Agent
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '4px' }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Quick suggestions */}
          <div style={{ background: '#f8fafc', padding: '8px 12px', borderBottom: '1px solid #e2e8f0', display: 'flex', gap: '6px', overflowX: 'auto' }}>
            {['How to submit?', 'How fast is AI?', 'Track my ticket', 'Accepted documents'].map((hint, i) => (
              <button
                key={i}
                onClick={() => handleSend(hint)}
                style={{
                  background: '#ffffff',
                  border: '1px solid #cbd5e1',
                  borderRadius: '12px',
                  padding: '4px 10px',
                  fontSize: '0.72rem',
                  color: '#1e40af',
                  fontWeight: '600',
                  whiteSpace: 'nowrap',
                  cursor: 'pointer'
                }}
              >
                {hint}
              </button>
            ))}
          </div>

          {/* Message List */}
          <div style={{ flex: 1, padding: '16px', overflowY: 'auto', background: '#fafafa', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '84%',
                  background: m.sender === 'user' ? '#1e40af' : '#ffffff',
                  color: m.sender === 'user' ? '#ffffff' : '#0f172a',
                  padding: '10px 14px',
                  borderRadius: m.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                  fontSize: '0.85rem',
                  lineHeight: '1.45',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
                  border: m.sender === 'user' ? 'none' : '1px solid #e2e8f0'
                }}
              >
                {m.text}
              </div>
            ))}
            {isTyping && (
              <div style={{ alignSelf: 'flex-start', background: '#ffffff', padding: '8px 14px', borderRadius: '12px', fontSize: '0.8rem', color: '#64748b', border: '1px solid #e2e8f0' }}>
                Nova is analyzing statutory guidelines...
              </div>
            )}
          </div>

          {/* Input Area */}
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            style={{
              padding: '12px 14px',
              background: '#ffffff',
              borderTop: '1px solid #e2e8f0',
              display: 'flex',
              gap: '8px',
              alignItems: 'center'
            }}
          >
            <input
              type="text"
              placeholder="Ask Nova how to use the portal..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{
                flex: 1,
                padding: '9px 12px',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                fontSize: '0.85rem',
                outline: 'none'
              }}
            />
            <button
              type="submit"
              disabled={!input.trim()}
              style={{
                background: '#1e40af',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '9px 12px',
                cursor: input.trim() ? 'pointer' : 'default',
                opacity: input.trim() ? 1 : 0.6
              }}
            >
              <Send size={15} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
