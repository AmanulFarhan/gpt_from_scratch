import { ArrowUpRight } from 'lucide-react'

export default function PromptCard({ children, onClick }) {
  return <button className="prompt-card" onClick={onClick}><span>{children}</span><ArrowUpRight size={15} /></button>
}
