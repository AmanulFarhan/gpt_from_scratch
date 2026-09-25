import { useRef } from 'react'
import { ArrowUp, CornerDownLeft } from 'lucide-react'

export default function ChatInput({ value, onChange, onSend, loading }) {
  const textarea = useRef(null)
  const submit = () => { if (!loading && value.trim()) { onSend(); if (textarea.current) textarea.current.style.height = 'auto' } }
  const handleKeyDown = event => {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit() }
  }
  const handleChange = event => {
    onChange(event.target.value)
    event.target.style.height = 'auto'
    event.target.style.height = `${Math.min(event.target.scrollHeight, 144)}px`
  }
  return <div className="composer-wrap"><form className="composer" onSubmit={event => { event.preventDefault(); submit() }}>
    <textarea ref={textarea} value={value} onChange={handleChange} onKeyDown={handleKeyDown} placeholder="Ask FlirtGPT something…" maxLength={2000} rows={1} aria-label="Message FlirtGPT" />
    <button className="send-button" type="submit" aria-label="Send message" disabled={loading || !value.trim()}><ArrowUp size={19} /></button>
  </form><div className="composer-hint"><span>Keep it curious.</span><span><kbd><CornerDownLeft size={10} /></kbd> Enter to send <span className="hint-divider">·</span> Shift + Enter for a new line</span></div></div>
}
