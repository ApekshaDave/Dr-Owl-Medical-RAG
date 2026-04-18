import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// ─── SVG Icons ────────────────────────────────────────────────────────────────
const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const ChevronIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

const DatabaseIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
  </svg>
);

const TargetIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <circle cx="12" cy="12" r="6" />
    <circle cx="12" cy="12" r="2" />
  </svg>
);

// ─── Simple Markdown Renderer (no external deps) ──────────────────────────────
function SimpleMarkdown({ text }) {
  if (!text) return null;
  const lines = text.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    if (line.trim() === '') { i++; continue; }

    if (/^(\s*[-*•]\s)/.test(line)) {
      const items = [];
      while (i < lines.length && /^(\s*[-*•]\s)/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*•]\s/, ''));
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} className="md-list">
          {items.map((item, j) => <li key={j}><InlineText text={item} /></li>)}
        </ul>
      );
      continue;
    }

    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\.\s/, ''));
        i++;
      }
      elements.push(
        <ol key={`ol-${i}`} className="md-list md-ordered">
          {items.map((item, j) => <li key={j}><InlineText text={item} /></li>)}
        </ol>
      );
      continue;
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.*)/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const Tag = `h${Math.min(level + 3, 6)}`;
      elements.push(
        <Tag key={`h-${i}`} className={`md-heading md-h${level}`}>
          <InlineText text={headingMatch[2]} />
        </Tag>
      );
      i++; continue;
    }

    if (/^---+$/.test(line.trim())) {
      elements.push(<hr key={`hr-${i}`} className="md-hr" />);
      i++; continue;
    }

    elements.push(
      <p key={`p-${i}`} className="md-p"><InlineText text={line} /></p>
    );
    i++;
  }

  return <div className="md-body">{elements}</div>;
}

function InlineText({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**'))
          return <strong key={i}>{part.slice(2, -2)}</strong>;
        if (part.startsWith('*') && part.endsWith('*'))
          return <em key={i}>{part.slice(1, -1)}</em>;
        if (part.startsWith('`') && part.endsWith('`'))
          return <code key={i} className="md-inline-code">{part.slice(1, -1)}</code>;
        return <span key={i}>{part}</span>;
      })}
    </>
  );
}

// ─── Relevance Score Components ───────────────────────────────────────────────

// Circular arc gauge for the overall score
function ScoreGauge({ score }) {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;
  const color = score >= 75 ? '#0d9488' : score >= 45 ? '#f59e0b' : '#ef4444';
  const label = score >= 75 ? 'High' : score >= 45 ? 'Medium' : 'Low';

  return (
    <div className="score-gauge-wrap">
      <svg width="72" height="72" viewBox="0 0 72 72" className="score-gauge-svg">
        {/* Track */}
        <circle
          cx="36" cy="36" r={radius}
          fill="none" stroke="rgba(0,0,0,0.07)" strokeWidth="6"
        />
        {/* Progress arc */}
        <circle
          cx="36" cy="36" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={`${progress} ${circumference}`}
          strokeDashoffset={circumference * 0.25}   /* start at top */
          style={{ transition: 'stroke-dasharray 0.8s cubic-bezier(.22,.68,0,1.2)' }}
        />
        {/* Score text */}
        <text x="36" y="33" textAnchor="middle" fontSize="13" fontWeight="700"
          fill={color} fontFamily="'Plus Jakarta Sans', sans-serif">
          {score}
        </text>
        <text x="36" y="46" textAnchor="middle" fontSize="7.5" fontWeight="500"
          fill={color} fontFamily="'Plus Jakarta Sans', sans-serif" opacity="0.8">
          {label}
        </text>
      </svg>
      <div className="score-gauge-label">Overall<br />Relevance</div>
    </div>
  );
}

// Inline mini bar for per-source score
function ScoreBar({ score, label }) {
  const color =
    label === 'High'   ? 'var(--score-high)'   :
    label === 'Medium' ? 'var(--score-mid)'     :
                         'var(--score-low)';
  const bg =
    label === 'High'   ? 'var(--score-high-bg)'   :
    label === 'Medium' ? 'var(--score-mid-bg)'     :
                         'var(--score-low-bg)';

  return (
    <div className="score-bar-wrap">
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{
            width: `${score}%`,
            background: color,
            transition: 'width 0.7s cubic-bezier(.22,.68,0,1.2)',
          }}
        />
      </div>
      <span className="score-bar-badge" style={{ background: bg, color }}>
        {label} · {score}
      </span>
    </div>
  );
}

// Full sources panel shown inside the accordion
function SourcesPanel({ sources, overallScore }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="sources-panel">
      <button className="sources-toggle" onClick={() => setOpen(o => !o)}>
        <span className="sources-toggle-left">
          <span className="sources-icon"><DatabaseIcon /></span>
          <span className="sources-toggle-label">
            Clinical Sources &amp; Relevance
          </span>
          <span className="sources-count">{sources.length} chunks</span>
        </span>
        <span className="sources-toggle-right">
          <ScoreGauge score={overallScore} />
          <span className={`sources-chevron ${open ? 'open' : ''}`}>
            <ChevronIcon />
          </span>
        </span>
      </button>

      {open && (
        <div className="sources-body">
          {sources.map((src) => (
            <div key={src.rank} className="source-item">
              <div className="source-item-header">
                <span className="source-rank">#{src.rank}</span>
                <span className="source-target"><TargetIcon /> Match</span>
                <ScoreBar score={src.score} label={src.label} />
                <span className="source-distance">
                  L2 dist: {src.distance}
                </span>
              </div>
              <div className="source-item-text">
                <SimpleMarkdown text={src.text} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const getTime = () =>
  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const SUGGESTIONS = [
  { icon: '🫀', text: 'What are the symptoms of a heart attack?' },
  { icon: '💊', text: 'Side effects of long-term ibuprofen use?' },
  { icon: '🧬', text: 'How does Type 2 diabetes develop?' },
  { icon: '🩺', text: 'When should I see a doctor for a fever?' },
];

// ─── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [input, setInput]             = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading]         = useState(false);
  const chatEndRef                    = useRef(null);
  const textareaRef                   = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, loading]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 130)}px`;
  }, [input]);

  const handleSend = async (overrideText) => {
    const query = (overrideText ?? input).trim();
    if (!query || loading) return;

    setChatHistory(prev => [...prev, { role: 'user', text: query, time: getTime() }]);
    setLoading(true);
    setInput('');

    try {
      const response = await fetch('https://pookiesdfsd-dr-owl-medical-rag.hf.space/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query }),
      });

      const data = await response.json();

      if (response.ok) {
        setChatHistory(prev => [...prev, {
          role:         'bot',
          text:         data.answer || "I'm sorry, I couldn't process that.",
          context:      data.context       || null,
          sources:      data.sources       || [],    // NEW
          overallScore: data.overall_score ?? null,  // NEW
          time:         getTime(),
        }]);
      } else {
        setChatHistory(prev => [...prev, {
          role:    'bot',
          text:    `**Backend Error ${response.status}:** ${data.detail || 'Unknown error.'}`,
          time:    getTime(),
          isError: true,
        }]);
      }
    } catch (err) {
      console.error('Network error:', err);
      setChatHistory(prev => [...prev, {
        role:    'bot',
        text:    '**Network Error:** Cannot reach the server. Make sure `api.py` is running on port 8000.',
        time:    getTime(),
        isError: true,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const isEmpty = chatHistory.length === 0;
  const canSend = input.trim().length > 0 && !loading;

  return (
    <div className="app-wrapper">

      {/* ── Navbar ──────────────────────────────────────────────────────── */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="brand-icon">🦉</div>
          <div className="brand-text">
            <span className="brand-name">Dr. Owl</span>
            <span className="brand-tag">Medical AI · 45K Records</span>
          </div>
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          Online
        </div>
      </nav>

      {/* ── Chat Window ─────────────────────────────────────────────────── */}
      <main className="chat-window" role="log" aria-live="polite">

        {isEmpty && (
          <div className="welcome-screen">
            <div className="welcome-glow" />
            <div className="welcome-icon-ring">
              <span className="welcome-owl">🦉</span>
            </div>
            <h1 className="welcome-title">How can I help you today?</h1>
            <p className="welcome-sub">
              Ask a medical question — I'll search a 45,000-record clinical knowledge base
              and show you exactly how relevant each source is.
            </p>
            <div className="disclaimer-badge">
              ⚠️ For educational use only. Always consult a qualified physician.
            </div>
            <div className="suggestions-grid">
              {SUGGESTIONS.map(s => (
                <button key={s.text} className="suggestion-chip" onClick={() => handleSend(s.text)}>
                  <span className="chip-icon">{s.icon}</span>
                  <span className="chip-text">{s.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {chatHistory.map((msg, index) => (
          <div key={index} className={`chat-row ${msg.role}`}>

            {msg.role === 'bot' && <div className="avatar bot-avatar">🦉</div>}

            <div className="message-group">
              <div className="role-label">
                {msg.role === 'user' ? 'You' : 'Dr. Owl'}
              </div>

              <div className={`message-bubble ${msg.isError ? 'error-bubble' : ''}`}>
                {msg.isError && <div className="error-header">⚠ Connection Problem</div>}
                <SimpleMarkdown text={msg.text} />
              </div>

              {/* ── Relevance Sources Panel (new) ── */}
              {msg.role === 'bot' && msg.sources && msg.sources.length > 0 && (
                <SourcesPanel
                  sources={msg.sources}
                  overallScore={msg.overallScore ?? 0}
                />
              )}

              {/* Fallback: plain context if no structured sources */}
              {msg.role === 'bot' && (!msg.sources || msg.sources.length === 0) && msg.context && (
                <details className="source-details">
                  <summary>
                    <span className="summary-chevron"><ChevronIcon /></span>
                    View Clinical Context
                  </summary>
                  <div className="source-text">
                    <SimpleMarkdown text={msg.context} />
                  </div>
                </details>
              )}

              <div className="msg-time">{msg.time}</div>
            </div>

            {msg.role === 'user' && (
              <div className="avatar user-avatar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="chat-row bot">
            <div className="avatar bot-avatar">🦉</div>
            <div className="message-group">
              <div className="role-label">Dr. Owl</div>
              <div className="message-bubble typing-bubble">
                <span className="typing-label">Searching knowledge base</span>
                <div className="typing-dots"><span /><span /><span /></div>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </main>

      {/* ── Input Footer ─────────────────────────────────────────────────── */}
      <footer className="input-area">
        <div className="input-shell">
          <div className={`input-box ${loading ? 'input-box-loading' : ''}`}>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your symptoms or ask a medical question…"
              disabled={loading}
              rows={1}
              aria-label="Medical question input"
            />
            <button
              className={`send-btn ${canSend ? 'send-btn-active' : ''}`}
              onClick={() => handleSend()}
              disabled={!canSend}
              aria-label="Send message"
            >
              {loading ? <span className="btn-spinner" /> : <SendIcon />}
            </button>
          </div>
          <p className="disclaimer-text">
            Dr. Owl provides educational insights only. Always consult a licensed physician.
            &nbsp;·&nbsp;
            <kbd>Enter</kbd> to send &nbsp; <kbd>Shift+Enter</kbd> for new line
          </p>
        </div>
      </footer>

    </div>
  );
}

export default App;