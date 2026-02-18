import { useState, useRef, useEffect } from 'react'
import { sendChatMessage } from '../api'

const SUGGESTED_QUERIES = [
  'What are our CPM benchmarks for Meta vs YouTube?',
  'Summarise the ITV airtime contract.',
  "What's our budget split by channel?",
  'Which month had the highest TV spend?',
]

function UserBubble({ text }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
      <div style={{
        maxWidth: '70%', padding: '10px 14px', borderRadius: '14px 14px 4px 14px',
        background: 'var(--accent)', color: '#fff', fontSize: 14, lineHeight: 1.5,
      }}>
        {text}
      </div>
    </div>
  )
}

function AssistantBubble({ text, loading }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 12 }}>
      <div style={{
        maxWidth: '70%', padding: '10px 14px', borderRadius: '14px 14px 14px 4px',
        background: 'var(--bg-surface)', border: '1px solid var(--border)',
        fontSize: 14, lineHeight: 1.5, color: 'var(--text)',
      }}>
        {loading ? (
          <span style={{ display: 'flex', gap: 4, alignItems: 'center', color: 'var(--text-muted)' }}>
            <span className="dot-pulse" style={{ display: 'inline-flex', gap: 3 }}>
              {[0, 1, 2].map(i => (
                <span key={i} style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: 'var(--text-muted)',
                  animation: `pulse 1.2s ${i * 0.2}s ease-in-out infinite`,
                }} />
              ))}
            </span>
          </span>
        ) : text}
      </div>
    </div>
  )
}

export default function RagChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend(query) {
    const text = (query || input).trim()
    if (!text || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setLoading(true)
    try {
      const reply = await sendChatMessage(text)
      setMessages(prev => [...prev, { role: 'assistant', text: reply }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'The RAG API is not yet connected. Start the backend at http://localhost:8000.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* Page header */}
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 22, fontWeight: 700, color: 'var(--text)' }}>RAG Chat</h1>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--text-muted)' }}>
          Ask questions over your embedded documents and marketing data.
        </p>
      </div>

      {/* Chat area */}
      <div style={{
        background: 'var(--bg-surface)', border: '1px solid var(--border)',
        borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column',
        minHeight: 480,
      }}>
        {/* Messages */}
        <div style={{ flex: 1, padding: '20px 20px 8px', overflowY: 'auto', minHeight: 360 }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', marginTop: 60 }}>
              <div style={{ fontSize: 32, marginBottom: 10 }}>💬</div>
              <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 20 }}>
                Ask anything about your data and documents.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                {SUGGESTED_QUERIES.map(q => (
                  <button
                    key={q}
                    onClick={() => handleSend(q)}
                    style={{
                      padding: '6px 12px', borderRadius: 20, border: '1px solid var(--border)',
                      background: 'var(--bg)', color: 'var(--text)', fontSize: 13,
                      cursor: 'pointer', transition: 'border-color 0.15s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((m, i) =>
                m.role === 'user'
                  ? <UserBubble key={i} text={m.text} />
                  : <AssistantBubble key={i} text={m.text} />
              )}
              {loading && <AssistantBubble loading />}
              <div ref={bottomRef} />
            </>
          )}
        </div>

        {/* Input bar */}
        <div style={{
          padding: '12px 16px', borderTop: '1px solid var(--border)',
          display: 'flex', gap: 8,
        }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask a question..."
            disabled={loading}
            style={{
              flex: 1, padding: '9px 14px', borderRadius: 8,
              border: '1px solid var(--border)', background: 'var(--bg)',
              color: 'var(--text)', fontSize: 14, outline: 'none',
              transition: 'border-color 0.15s',
            }}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            style={{
              padding: '9px 18px', borderRadius: 8, border: 'none',
              background: input.trim() && !loading ? 'var(--accent)' : 'var(--border)',
              color: input.trim() && !loading ? '#fff' : 'var(--text-muted)',
              cursor: input.trim() && !loading ? 'pointer' : 'not-allowed',
              fontSize: 14, fontWeight: 600, transition: 'background 0.15s',
            }}
          >
            Send
          </button>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  )
}
