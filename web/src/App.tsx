import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import AgentSelectPage from './pages/AgentSelectPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  const [token, setToken] = useState<string | null>(
    sessionStorage.getItem('rv_token')
  )
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  const handleLogin = (t: string) => {
    sessionStorage.setItem('rv_token', t)
    setToken(t)
  }

  const handleLogout = () => {
    sessionStorage.removeItem('rv_token')
    setToken(null)
    setSelectedAgent(null)
  }

  if (!token) return <LoginPage onLogin={handleLogin} />
  if (!selectedAgent) return <AgentSelectPage onSelect={setSelectedAgent} onLogout={handleLogout} />
  return <ChatPage token={token} onLogout={handleLogout} onBack={() => setSelectedAgent(null)} />
}
