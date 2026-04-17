import { useState, useRef, useEffect } from "react";
import ReactMarkdown from 'react-markdown';

// ─── SVG Icons ───────────────────────────────────────────────────────────────

const SendIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" />
    <polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const BotIcon = () => (
  <svg viewBox="0 0 100 100" className="w-6 h-6 text-teal-700" fill="currentColor">
    <path d="M50 10c-8.8 0-16.7 3.6-22.3 9.4-1.3 1.4-1.3 3.6 0 5 1.4 1.3 3.6 1.3 5 0 4.3-4.5 10.4-7.2 17.3-7.2s13 2.8 17.3 7.2c1.4 1.3 3.6 1.3 5 0 1.3-1.4 1.3-3.6 0-5C66.7 13.6 58.8 10 50 10zM50 30c-5.5 0-10 4.5-10 10s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10zM50 80c5.5 0 10-4.5 10-10s-4.5-10-10-10-10 4.5-10 10 4.5 10 10 10zM80 50c0-16.6-13.4-30-30-30s-30 13.4-30 30 13.4 30 30 30 30-13.4 30-30zm-30 20c-11 0-20-9-20-20s9-20 20-20 20 9 20 20-9 20-20 20z"></path>
  </svg>
);

const UserIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const AlertIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" className="w-4 h-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

// ─── Sub-Components ──────────────────────────────────────────────────────────

const TypingIndicator = () => (
  <div className="flex items-end gap-3 mb-6 animate-fadeIn">
    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-100 border border-teal-200 flex items-center justify-center text-teal-600 shadow-sm">
      <BotIcon />
    </div>
    <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-5 py-4 shadow-sm">
      <div className="flex items-center gap-1.5">
        <span className="block w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="block w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="block w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  </div>
);

const MessageBubble = ({ message }) => {
  const isUser = message.role === "user";
  const isError = message.isError;

  return (
    <div className={`flex items-end gap-3 mb-6 ${isUser ? "justify-end animate-slideInRight" : "animate-slideInLeft"}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-100 border border-teal-200 flex items-center justify-center text-teal-600 shadow-sm">
          <BotIcon />
        </div>
      )}
      <div className={`max-w-[75%] md:max-w-[70%] ${isUser ? "text-right" : ""}`}>
        <div className={`rounded-2xl px-5 py-3.5 shadow-sm ${
          isUser 
            ? "bg-gradient-to-br from-teal-500 to-teal-600 text-white rounded-br-sm" 
            : isError ? "bg-red-50 border border-red-200 text-red-700 rounded-bl-sm" : "bg-white border border-slate-200 text-slate-700 rounded-bl-sm"
        }`}>
          {isError && (
            <div className="flex items-center gap-2 mb-2 text-red-500 font-medium text-xs uppercase tracking-wider">
              <AlertIcon /> Error
            </div>
          )}
          <div className="text-sm md:text-base leading-relaxed font-light space-y-2 text-left">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
          {message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100 text-left">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Retrieved Context</p>
              <div className="flex flex-col gap-2">
                {message.sources.map((src, idx) => (
                  <div key={idx} className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs text-slate-600">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-medium text-teal-700">{src.document_name}</span>
                      <span className="bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full text-[10px]">Score: {src.score}</span>
                    </div>
                    <div className="italic text-slate-500 line-clamp-2 text-[11px]">"{src.text}"</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <p className="text-[10px] text-slate-400 mt-1.5 px-1">{message.timestamp}</p>
      </div>
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-teal-500 flex items-center justify-center text-white shadow-md shadow-teal-100">
          <UserIcon />
        </div>
      )}
    </div>
  );
};

const WelcomeScreen = () => (
  <div className="flex flex-col items-center justify-center h-full text-center px-8 animate-fadeIn">
    <div className="relative mb-8">
      <div className="absolute inset-0 rounded-full bg-teal-100 animate-ping opacity-30" style={{ animationDuration: "3s" }} />
      <div className="relative w-28 h-28 rounded-full bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center shadow-lg shadow-teal-200 border-4 border-white/20">
        <span className="text-6xl select-none">🦉</span>
      </div>
    </div>
    <h2 className="text-2xl md:text-3xl font-semibold text-slate-700 mb-3 tracking-tight">I'm Dr. Owl, your medical AI</h2>
    <p className="text-slate-400 text-sm md:text-base max-w-md leading-relaxed mb-10">Wisely analyzing your health questions using professional medical datasets.</p>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
      {[
        { icon: "💊", text: "What are common side effects of ibuprofen?" },
        { icon: "🫀", text: "Explain the symptoms of hypertension" },
        { icon: "🧬", text: "How does type 2 diabetes develop?" },
        { icon: "🩸", text: "What do high WBC levels indicate?" },
      ].map((s) => (
        <button key={s.text} className="flex items-start gap-3 text-left p-4 rounded-xl bg-white border border-slate-200 hover:border-teal-300 hover:shadow-md transition-all duration-200 group cursor-pointer" onClick={() => document.getElementById("chat-input")?.dispatchEvent(new CustomEvent("suggestionClick", { detail: s.text, bubbles: true }))}>
          <span className="text-xl mt-0.5 flex-shrink-0">{s.icon}</span>
          <span className="text-sm text-slate-600 group-hover:text-teal-700 transition-colors leading-snug">{s.text}</span>
        </button>
      ))}
    </div>
  </div>
);

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, isLoading]);

  useEffect(() => {
    const el = document.getElementById("chat-input");
    const handler = (e) => setInput(e.detail);
    el?.addEventListener("suggestionClick", handler);
    return () => el?.removeEventListener("suggestionClick", handler);
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((prev) => [...prev, { role: "user", content: input, timestamp }]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentInput }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.answer, sources: data.sources || [], timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Connection Error: Check if backend is running.", isError: true, timestamp }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
        body { font-family: 'DM Sans', sans-serif; background: #f1f5f9; margin: 0; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes slideInRight { from { opacity: 0; transform: translateX(16px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes slideInLeft { from { opacity: 0; transform: translateX(-16px); } to { opacity: 1; transform: translateX(0); } }
        .animate-fadeIn { animation: fadeIn .35s ease both; }
        .animate-slideInRight { animation: slideInRight .3s ease both; }
        .animate-slideInLeft { animation: slideInLeft .3s ease both; }
        .chat-scroll::-webkit-scrollbar { width: 6px; }
        .chat-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        .header-gradient { background: linear-gradient(135deg, #134e4a 0%, #0e7490 100%); }
      `}</style>

      <div className="flex flex-col h-screen bg-slate-100">
        <header className="header-gradient text-white px-6 py-4 flex items-center justify-between shadow-lg z-10 flex-shrink-0">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center text-2xl">🦉</div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight leading-none">Dr Owl</h1>
              <p className="text-teal-200 text-xs mt-0.5 font-light">Medical Knowledge Assistant</p>
            </div>
          </div>
          <div className="flex items-center gap-2 bg-white/10 rounded-full px-3 py-1.5 border border-white/10">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-xs text-teal-100 font-medium tracking-wide">Online</span>
          </div>
        </header>

        <div className="bg-white/50 border-b border-slate-200 px-4 py-2 flex items-center justify-center gap-2 flex-shrink-0">
          <span className="text-amber-500 text-xs">⚠️</span>
          <p className="text-[11px] text-slate-500 text-center font-medium uppercase tracking-tight">For informational purposes only. Consult a doctor.</p>
        </div>

        <main className="flex-1 overflow-y-auto chat-scroll px-4 py-6">
          <div className="max-w-3xl mx-auto h-full">
            {messages.length === 0 ? <WelcomeScreen /> : (
              <>
                {messages.map((msg, i) => <MessageBubble key={i} message={msg} />)}
                {isLoading && <TypingIndicator />}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>
        </main>

        <footer className="bg-white border-t border-slate-200 px-4 py-4 flex-shrink-0 shadow-lg">
          <div className="max-w-3xl mx-auto">
            <div className={`flex items-end gap-3 rounded-2xl border bg-white px-4 py-3 transition-all ${isLoading ? "border-slate-100 opacity-80" : "border-slate-300 focus-within:border-teal-400 shadow-sm"}`}>
              <textarea 
                id="chat-input" 
                ref={textareaRef} 
                rows={1} 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), sendMessage())} 
                disabled={isLoading} 
                placeholder="Ask Dr. Owl a medical question…" 
                className="flex-1 resize-none bg-transparent text-slate-700 text-sm md:text-base outline-none disabled:opacity-50 py-1" 
              />
              <button onClick={sendMessage} disabled={!input.trim() || isLoading} className={`w-10 h-10 rounded-xl flex items-center justify-center text-white transition-all ${ input.trim() && !isLoading ? "bg-teal-600 hover:bg-teal-700 shadow-md" : "bg-slate-200 text-slate-400"}`}>
                {isLoading ? <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <SendIcon />}
              </button>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}