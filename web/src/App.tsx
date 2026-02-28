import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import AgentSelectPage from './pages/AgentSelectPage'
import ChatPage from './pages/ChatPage'
import DealsPage from './pages/DealsPage'
import AsksPage from './pages/AsksPage'
import CompaniesPage from './pages/CompaniesPage'
import ExpertsPage from './pages/ExpertsPage'
import NewslettersPage from './pages/NewslettersPage'

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

  const handleBack = () => setSelectedAgent(null)

  if (!token) return <LoginPage onLogin={handleLogin} />
  if (!selectedAgent) return <AgentSelectPage token={token} onSelect={setSelectedAgent} onLogout={handleLogout} />

  if (selectedAgent === 'deals') {
    return <DealsPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

  if (selectedAgent === 'asks') {
    return <AsksPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

  if (selectedAgent === 'experts') {
    return <ExpertsPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

  if (selectedAgent === 'companies') {
    return <CompaniesPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

  if (selectedAgent === 'newsletters') {
    return <NewslettersPage onLogout={handleLogout} onBack={handleBack} />
  }

  return <ChatPage token={token} onLogout={handleLogout} onBack={handleBack} />
}
