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
  const [isHovered, setIsHovered] = useState(false);
  const [twirlActive, setTwirlActive] = useState(false);

  // Smooth cyclic robotic movements: subtle breathing, joyful head tilt, waving arm, antenna pulse
  useEffect(() => {
    const timer = setInterval(() => {
      setMotionFrame(prev => (prev + 1) % 6);
    }, 700);
    return () => clearInterval(timer);
  }, []);

  const triggerTwirl = (e) => {
    e.stopPropagation();
    setTwirlActive(true);
    setTimeout(() => setTwirlActive(false), 900);
    setIsOpen(prev => !prev);
  };

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

  // Movement parameters based on frame
  const floatOffset = [0, -3, -6, -4, -1, 1][motionFrame];
  const headAngle = isHovered ? -6 : [0, -4, 0, 4, 2, -2][motionFrame];
  const leftArmWave = isHovered ? -45 : [-10, -28, -42, -25, -12, 0][motionFrame];
  const rightArmAngle = isHovered ? 20 : [0, 5, 8, 4, 0, -2][motionFrame];
  const eyeGlowColor = isTyping ? '#fbbf24' : (isHovered ? '#38bdf8' : '#60a5fa');

  return (
    <>
      <style>{`
        @keyframes subtleAntennaPulse {
          0%, 100% { transform: scale(1); filter: drop-shadow(0 0 4px #38bdf8); }
          50% { transform: scale(1.3); filter: drop-shadow(0 0 10px #60a5fa); }
        }
        @keyframes novaTwirlSpin {
          0% { transform: rotate(0deg) scale(1); }
          50% { transform: rotate(180deg) scale(1.15) translateY(-8px); }
          100% { transform: rotate(360deg) scale(1); }
        }
        .nova-twirl {
          animation: novaTwirlSpin 0.85s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }
      `}</style>

      {/* ── COMPACT FLOATING NOVA BOT WITH FLUID GESTURES & TWIRL ── */}
      <div
        onClick={triggerTwirl}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
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
        title="Click Nova to chat or twirl!"
      >
        {!isOpen && (
          <div style={{
            background: '#0f172a',
            color: '#ffffff',
            padding: '7px 14px',
            borderRadius: '20px',
            fontSize: '0.8rem',
            fontWeight: '600',
            boxShadow: '0 6px 16px rgba(0,0,0,0.22)',
            border: '1px solid rgba(255,255,255,0.18)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'transform 0.2s ease, box-shadow 0.2s ease',
            transform: isHovered ? 'scale(1.04)' : 'scale(1)'
          }}>
            <Sparkles size={14} color="#38bdf8" />
            <span>Chat with <strong>Nova</strong></span>
          </div>
        )}

        {/* ── CUTE ROBOT BODY WITH TWIRL ANIMATION ── */}
        <div 
          className={twirlActive ? 'nova-twirl' : ''}
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            transform: twirlActive ? undefined : `translateY(${floatOffset}px) scale(${isHovered ? 1.08 : 1})`,
            transition: twirlActive ? 'none' : 'transform 0.35s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        >
          {/* Small Antenna */}
          <div style={{
            width: '3px',
            height: '8px',
            background: '#94a3b8',
            borderRadius: '2px',
            position: 'relative',
            display: 'flex',
            justifyContent: 'center'
          }}>
            <div style={{
              position: 'absolute',
              top: '-6px',
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              background: '#38bdf8',
              boxShadow: '0 0 8px #38bdf8',
              animation: 'subtleAntennaPulse 1.8s infinite'
            }}></div>
          </div>

          {/* Smooth Curved Robot Head with Headphones / Ear Caps */}
          <div style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transform: `rotate(${headAngle}deg)`,
            transition: 'transform 0.35s ease'
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
              width: '40px',
              height: '30px',
              borderRadius: '15px',
              background: 'linear-gradient(135deg, #ffffff 40%, #e2e8f0 100%)',
              border: '1.5px solid #cbd5e1',
              boxShadow: '0 4px 10px rgba(0,0,0,0.14)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Visor Screen with Glowing Cyan Eyes & Smile */}
              <div style={{
                width: '30px',
                height: '19px',
                borderRadius: '10px',
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
                    boxShadow: `0 0 6px ${eyeGlowColor}`
                  }}></div>
                  <div style={{
                    width: '4px',
                    height: '5px',
                    borderRadius: '50%',
                    background: eyeGlowColor,
                    boxShadow: `0 0 6px ${eyeGlowColor}`
                  }}></div>
                </div>

                {/* Cute Smiling Mouth */}
                <div style={{
                  width: '7px',
                  height: '3px',
                  borderRadius: '0 0 5px 5px',
                  borderBottom: `1.5px solid ${eyeGlowColor}`
                }}></div>
              </div>
            </div>
          </div>

          {/* Neck Ring */}
          <div style={{
            width: '15px',
            height: '2.5px',
            background: '#93c5fd',
            borderRadius: '2px',
            margin: '0.5px 0'
          }}></div>

          {/* Cute Round Body with Fluid Moving Arms */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1px' }}>
            {/* Left Arm (Waving Motion) */}
            <div style={{
              width: '5px',
              height: '17px',
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
              width: '30px',
              height: '24px',
              borderRadius: '13px 13px 15px 15px',
              background: 'linear-gradient(135deg, #ffffff 40%, #f1f5f9 100%)',
              border: '1.5px solid #cbd5e1',
              boxShadow: '0 4px 10px rgba(0,0,0,0.12)',
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
                boxShadow: '0 0 5px #3b82f6'
              }}></div>
            </div>

            {/* Right Arm */}
            <div style={{
              width: '5px',
              height: '16px',
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
          <div style={{ display: 'flex', gap: '7px', marginTop: '1px' }}>
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

      {/* ── CHAT MODAL ── */}
      {isOpen && (
        <div style={{
          position: 'fixed',
          bottom: '88px',
          right: '24px',
          width: '380px',
          maxHeight: '520px',
          background: '#ffffff',
          borderRadius: '16px',
          boxShadow: '0 12px 32px rgba(0,0,0,0.22)',
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          zIndex: 9999,
          overflow: 'hidden'
        }} className="tab-pane-fade">
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%)',
            color: '#ffffff',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: '#22c55e',
                boxShadow: '0 0 6px #22c55e'
              }}></div>
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: '700' }}>Nova AI Sentinel</div>
                <div style={{ fontSize: '0.72rem', color: '#93c5fd' }}>RBI Redressal Autonomous Bot</div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#ffffff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '4px'
              }}
            >
              <X size={18} />
            </button>
          </div>

          {/* Messages Container */}
          <div style={{
            padding: '14px',
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px',
            background: '#f8fafc',
            maxHeight: '340px'
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
                  maxWidth: '82%',
                  padding: '9px 13px',
                  borderRadius: m.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                  background: m.sender === 'user' ? '#1e40af' : '#ffffff',
                  color: m.sender === 'user' ? '#ffffff' : '#0f172a',
                  border: m.sender === 'user' ? 'none' : '1px solid #e2e8f0',
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
