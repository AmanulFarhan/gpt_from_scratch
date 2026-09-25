import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'
import TypingIndicator from './TypingIndicator.jsx'

export default function MessageList({ messages, loading }) {
  const bottom = useRef(null)
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, loading])
  return <div className="message-list" aria-live="polite">
    {messages.map((message, index) => <MessageBubble key={`${index}-${message.role}`} message={message} />)}
    {loading && <TypingIndicator />}
    <div ref={bottom} />
  </div>
}
