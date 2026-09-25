import { Heart } from 'lucide-react'

export default function TypingIndicator() {
  return <div className="message-row assistant-row" role="status" aria-label="FlirtGPT is thinking">
    <div className="message-avatar"><Heart size={14} /></div>
    <div className="typing-bubble"><span>FlirtGPT is thinking</span><i /><i /><i /></div>
  </div>
}
