import { Heart } from 'lucide-react'

export function cleanMessage(value) {
  return value.replace(/<\|(?:user|assistant)\|>/g, '').replace(/<\|[^|]+\|>/g, '').trim()
}

export default function MessageBubble({ message }) {
  const assistant = message.role === 'assistant'
  return <article className={`message-row ${assistant ? 'assistant-row' : 'user-row'}`}>
    {assistant && <div className="message-avatar" aria-label="FlirtGPT"><Heart size={14} /></div>}
    <div className={`message-bubble ${assistant ? 'assistant-bubble' : 'user-bubble'}`}>{cleanMessage(message.content)}</div>
  </article>
}
