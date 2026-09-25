import { Heart, Plus } from 'lucide-react'

export default function ChatHeader({ onNewChat }) {
  return <header className="chat-header">
    <a className="brand" href="#top" aria-label="FlirtGPT home">
      <span className="brand-mark"><Heart size={17} strokeWidth={2.1} /></span>
      <span className="brand-copy"><strong>FlirtGPT</strong><small>A GPT built from scratch.</small></span>
    </a>
    <div className="header-actions"><span className="model-status"><i /> V1 model</span><button className="new-chat" onClick={onNewChat}><Plus size={16} /><span>New chat</span></button></div>
  </header>
}
