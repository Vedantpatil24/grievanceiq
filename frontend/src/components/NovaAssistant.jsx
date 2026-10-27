import React, { useState, useEffect } from 'react';
import { Bot, X, Send, Sparkles } from 'lucide-react';

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
  const [motionFrame, setMotionFrame] = useState(0);

  // Smooth cyclic robotic movements: subtle breathing, joyful head tilt, waving arm, antenna pulse
  useEffect(() => {
    const timer = setInterval(() => {
      setMotionFrame(prev => (prev + 1) % 6);
    }, 800);
    return () => clearInterval(timer);
  }, []);

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query) return;

    const newMsgs = [...messages, { sender: 'user', text: query }];
    setMessages(newMsgs);
    if (!textToSend) setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/ai/assistant-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      });
      if (!res.ok) throw new Error('API failed');
      const data = await res.json();
      setMessages([...newMsgs, { sender: 'nova', text: data.reply || "I am processing your grievance inquiry." }]);
    } catch (err) {
      const q = query.toLowerCase();
      let reply = "GrievanceIQ is an AI-powered financial dispute redressal platform compliant with RBI regulations. You can submit complaints, track live audit trails, verify evidence with OCR, and simulate operational staffing across Indian banking institutions.";
      if (q.includes('submit') || q.includes('file') || q.includes('lodge')) {
        reply = "To submit a grievance: Click 'Submit Complaint' in the top bar. Pick your bank, choose the dispute category, input transaction reference (UTR), and attach payment proof (PNG/PDF).";
      } else if (q.includes('track') || q.includes('status')) {
        reply = "To track an existing case: Go to 'Track Complaint' and enter your ticket token (e.g. GRV-2026-15011) to inspect real-time audit trails.";
      }
      setMessages([...newMsgs, { sender: 'nova', text: reply }]);
    } finally {
      setIsTyping(false);
    }
  };

  // Movement parameters based on reference 3D robot image
  const floatOffset = [0, -3, -5, -4, -1, 1][motionFrame];
  const headAngle = [0, -4, 0, 4, 2, -2][motionFrame];
  const leftArmWave = [-10, -28, -38, -25, -12, 0][motionFrame];
  const rightArmAngle = [0, 5, 8, 4, 0, -2][motionFrame];
  const eyeGlowColor = isTyping ? '#fbbf24' : '#38bdf8';

  return (
    <>
      <style>{`
        @keyframes subtleAntennaPulse {
          0%, 100% { transform: scale(1); filter: drop-shadow(0 0 4px #38bdf8); }
          50% { transform: scale(1.2); filter: drop-shadow(0 0 8px #60a5fa); }
        }
      `}</style>

      {/* ── COMPACT FLOATING NOVA BOT (MATCHING WHITE/BLUE AESTHETIC) ── */}
      <div
        onClick={() => setIsOpen(prev => !prev)}
        style={{
          position: 'fixed',
          bottom: '22px',
          right: '24px',
          zIndex: 9999,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          userSelect: 'none'
        }}
        title="Chat with Nova AI Sentinel"
      >
        {!isOpen && (
          <div style={{
            background: '#0f172a',
            color: '#ffffff',
            padding: '6px 12px',
            borderRadius: '16px',
            fontSize: '0.78rem',
            fontWeight: '600',
            boxShadow: '0 4px 12px rgba(0,0,0,0.18)',
            border: '1px solid rgba(255,255,255,0.15)',
            display: 'flex',
            alignItems: 'center',
            gap: '5px'
          }}>
            <Sparkles size={13} color="#38bdf8" />
            <span>Chat with <strong>Nova</strong></span>
          </div>
        )}

        {/* ── CUTE COMPACT ROBOT BODY ── */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          transform: `translateY(${floatOffset}px)`,
          transition: 'transform 0.4s ease-in-out'
        }}>
          {/* Small Antenna */}
          <div style={{
            width: '3px',
            height: '7px',
            background: '#94a3b8',
            borderRadius: '2px',
            position: 'relative',
            display: 'flex',
            justifyContent: 'center'
          }}>
            <div style={{
              position: 'absolute',
              top: '-5px',
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#38bdf8',
              boxShadow: '0 0 6px #38bdf8',
              animation: 'subtleAntennaPulse 2s infinite'
            }}></div>
          </div>

          {/* Smooth Curved Robot Head with Headphones / Ear Caps */}
          <div style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `rotate(${headAngle}deg)`,
            transition: 'transform 0.4s ease'
          }}>
            {/* Ear Caps (Left & Right) */}
            <div style={{
              position: 'absolute',
              left: '-4px',
              width: '6px',
              height: '14px',
              borderRadius: '4px',
              background: '#93c5fd',
              boxShadow: '0 1px 3px rgba(0,0,0,0.15)'
            }}></div>
            <div style={{
              position: 'absolute',
              right: '-4px',
              width: '6px',
              height: '14px',
              borderRadius: '4px',
              background: '#93c5fd',
              boxShadow: '0 1px 3px rgba(0,0,0,0.15)'
            }}></div>

            {/* White Helmet Dome */}
            <div style={{
              width: '38px',
              height: '28px',
              borderRadius: '14px',
              background: 'linear-gradient(135deg, #ffffff 40%, #e2e8f0 100%)',
              border: '1.5px solid #cbd5e1',
              boxShadow: '0 3px 8px rgba(0,0,0,0.12)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Visor Screen with Glowing Cyan Eyes & Smile */}
              <div style={{
                width: '28px',
                height: '18px',
                borderRadius: '9px',
                background: '#0f172a',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '2px',
                boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.5)'
              }}>
                {/* Eyes */}
                <div style={{ display: 'flex', gap: '6px' }}>
                  <div style={{
                    width: '4px',
                    height: '5px',
                    borderRadius: '50%',
                    background: eyeGlowColor,
                    boxShadow: `0 0 5px ${eyeGlowColor}`
                  }}></div>
                  <div style={{
                    width: '4px',
                    height: '5px',
                    borderRadius: '50%',
                    background: eyeGlowColor,
                    boxShadow: `0 0 5px ${eyeGlowColor}`
                  }}></div>
                </div>

                {/* Cute Smiling Mouth */}
                <div style={{
                  width: '6px',
                  height: '3px',
                  borderRadius: '0 0 5px 5px',
                  borderBottom: `1.5px solid ${eyeGlowColor}`
                }}></div>
              </div>
            </div>
          </div>

          {/* Neck Ring */}
          <div style={{
            width: '14px',
            height: '2.5px',
            background: '#93c5fd',
            borderRadius: '2px',
            margin: '0.5px 0'
          }}></div>

          {/* Cute Round Body with Arms */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1px' }}>
            {/* Left Arm (Waving Motion) */}
            <div style={{
              width: '5px',
              height: '16px',
              borderRadius: '4px',
              background: '#ffffff',
              border: '1px solid #cbd5e1',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              transformOrigin: 'top center',
              transform: `rotate(${leftArmWave}deg)`,
              transition: 'transform 0.3s ease'
            }}></div>

            {/* Pear-shaped Chubby Torso */}
            <div style={{
              width: '28px',
              height: '22px',
              borderRadius: '12px 12px 14px 14px',
              background: 'linear-gradient(135deg, #ffffff 40%, #f1f5f9 100%)',
              border: '1.5px solid #cbd5e1',
              boxShadow: '0 3px 8px rgba(0,0,0,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Cute Blue Chest Emblem */}
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: '#3b82f6',
                border: '1px solid #ffffff',
                boxShadow: '0 0 4px #3b82f6'
              }}></div>
            </div>

            {/* Right Arm */}
            <div style={{
              width: '5px',
              height: '15px',
              borderRadius: '4px',
              background: '#ffffff',
              border: '1px solid #cbd5e1',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              transformOrigin: 'top center',
              transform: `rotate(${rightArmAngle}deg)`,
              transition: 'transform 0.3s ease'
            }}></div>
          </div>

          {/* Little White Feet */}
          <div style={{ display: 'flex', gap: '6px', marginTop: '1px' }}>
            <div style={{
              width: '7px',
              height: '5px',
              borderRadius: '3px',
              background: '#cbd5e1',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}></div>
            <div style={{
              width: '7px',
              height: '5px',
              borderRadius: '3px',
              background: '#cbd5e1',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}></div>
          </div>
        </div>
      </div>

      {/* ── CHAT MODAL WINDOW ── */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '88px',
          right: '24px',
          width: '380px',
          height: '510px',
          background: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 16px 40px rgba(0,0,0,0.25)',
          zIndex: 10000,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          border: '1px solid #e2e8f0',
          animation: 'fadeInUp 0.3s ease'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #0f172a, #1e3a8a)',
            padding: '14px 16px',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                background: 'rgba(255,255,255,0.15)',
                padding: '7px',
                borderRadius: '50%',
                display: 'flex'
              }}>
                <Bot size={20} color="#38bdf8" />
              </div>
              <div>
                <div style={{ fontWeight: '700', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  Nova-AI Sentinel
                  <span style={{
                    fontSize: '0.62rem',
                    background: '#10b981',
                    color: '#ffffff',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    fontWeight: '600'
                  }}>ONLINE</span>
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>RBI Grievance Compliance Assistant</div>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Quick FAQ Chips */}
          <div style={{
            background: '#f8fafc',
            padding: '8px 12px',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            gap: '6px',
            overflowX: 'auto',
            whiteSpace: 'nowrap'
          }}>
            <button
              onClick={() => handleSend("How many total complaints are in the database?")}
              style={{
                background: '#ffffff',
                border: '1px solid #cbd5e1',
                padding: '4px 10px',
                borderRadius: '14px',
                fontSize: '0.72rem',
                color: '#334155',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Sparkles size={12} color="#2563eb" /> System Stats
            </button>

            <button
              onClick={() => handleSend("Paise cut ho gaye atm se cash nahi nikla kya karu?")}
              style={{
                background: '#ffffff',
                border: '1px solid #cbd5e1',
                padding: '4px 10px',
                borderRadius: '14px',
                fontSize: '0.72rem',
                color: '#334155',
                cursor: 'pointer'
              }}
            >
              ATM Cash Issue
            </button>

            <button
              onClick={() => handleSend("What is the RBI turnaround time and compensation for failed UPI?")}
              style={{
                background: '#ffffff',
                border: '1px solid #cbd5e1',
                padding: '4px 10px',
                borderRadius: '14px',
                fontSize: '0.72rem',
                color: '#334155',
                cursor: 'pointer'
              }}
            >
              RBI TAT & Rules
            </button>
          </div>

          {/* Message History */}
          <div style={{
            flex: 1,
            padding: '14px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px'
          }}>
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: m.sender === 'user' ? 'flex-end' : 'flex-start'
                }}
              >
                <div style={{
                  maxWidth: '84%',
                  padding: '9px 13px',
                  borderRadius: m.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                  background: m.sender === 'user' ? '#2563eb' : '#f1f5f9',
                  color: m.sender === 'user' ? '#ffffff' : '#0f172a',
                  fontSize: '0.84rem',
                  lineHeight: '1.45',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  wordBreak: 'break-word'
                }}>
                  {m.text}
                </div>
              </div>
            ))}

            {isTyping && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  padding: '7px 12px',
                  borderRadius: '12px 12px 12px 2px',
                  background: '#f1f5f9',
                  color: '#64748b',
                  fontSize: '0.78rem',
                  fontStyle: 'italic'
                }}>
                  Nova is thinking...
                </div>
              </div>
            )}
          </div>

          {/* Input Bar */}
          <div style={{
            padding: '10px 12px',
            borderTop: '1px solid #e2e8f0',
            display: 'flex',
            gap: '8px',
            background: '#ffffff'
          }}>
            <input
              type="text"
              placeholder="Ask Nova anything about your grievance, rules..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              style={{
                flex: 1,
                padding: '9px 12px',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                fontSize: '0.84rem',
                outline: 'none'
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={isTyping || !input.trim()}
              style={{
                background: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                width: '38px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                opacity: input.trim() ? 1 : 0.6
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
