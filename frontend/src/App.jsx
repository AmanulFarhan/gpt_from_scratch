import { useState } from 'react'
import ChatHeader from './components/ChatHeader.jsx'
import ChatInput from './components/ChatInput.jsx'
import MessageList from './components/MessageList.jsx'
import WelcomeScreen from './components/WelcomeScreen.jsx'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const sendMessage = async (override = '') => {
    const content = (override || input).trim()
    if (!content || loading) return
    const nextMessages = [...messages, { role: 'user', content }]
    setMessages(nextMessages)
    setInput('')
    setError('')
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, history: messages }),
      })
      if (!response.ok) throw new Error('Chat request failed')
      const data = await response.json()
      if (typeof data.response !== 'string' || !data.response.trim()) throw new Error('Empty model response')
      setMessages([...nextMessages, { role: 'assistant', content: data.response }])
    } catch {
      setError('FlirtGPT is taking a little break. Try again in a moment.')
    } finally { setLoading(false) }
  }

  const newChat = () => { setMessages([]); setInput(''); setError('') }

  return <main className="app-shell" id="top">
    <ChatHeader onNewChat={newChat} />
    <section className="chat-stage" aria-label="Conversation">
      {messages.length === 0 ? <WelcomeScreen onPrompt={sendMessage} /> : <MessageList messages={messages} loading={loading} />}
    </section>
    <footer className="input-dock">
      {error && <div className="error-message" role="alert">{error}</div>}
      <ChatInput value={input} onChange={setInput} onSend={() => sendMessage()} loading={loading} />
      <p className="fine-print">A small model with a big imagination. Responses may be a little unexpected.</p>
    </footer>
  </main>
}
