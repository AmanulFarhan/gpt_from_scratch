import { Heart } from 'lucide-react'
import PromptCard from './PromptCard.jsx'

const prompts = ['How was your day?', 'You seem pretty confident.', 'Tell me something interesting.', 'I had a terrible day.']

export default function WelcomeScreen({ onPrompt }) {
  return <div className="welcome-screen">
    <div className="welcome-mark"><Heart size={24} /></div>
    <p className="eyebrow">A LITTLE SPARK OF SOMETHING</p>
    <h1>Meet <span>FlirtGPT.</span></h1>
    <p className="welcome-copy">A tiny GPT built from scratch,<br className="desktop-break" /> with a little personality.</p>
    <div className="prompt-grid">{prompts.map(prompt => <PromptCard key={prompt} onClick={() => onPrompt(prompt)}>{prompt}</PromptCard>)}</div>
  </div>
}
