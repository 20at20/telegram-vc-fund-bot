import { useState } from 'react'
import posthog from 'posthog-js'
import LoginPage from './pages/LoginPage'
import AgentSelectPage from './pages/AgentSelectPage'
import ChatPage from './pages/ChatPage'
import LPChatPage from './pages/LPChatPage'
import DealsPage from './pages/DealsPage'
import AsksPage from './pages/AsksPage'
import CompaniesPage from './pages/CompaniesPage'
import ExpertsPage from './pages/ExpertsPage'
import SubmitDealPage from './pages/SubmitDealPage'
import FundDocsPage from './pages/FundDocsPage'

export default function App() {
  const [token, setToken] = useState<string | null>(
    sessionStorage.getItem('rv_token')
  )
  const [username, setUsername] = useState<string>(
    sessionStorage.getItem('rv_username') || ''
  )
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  const handleLogin = (t: string, user: string) => {
    sessionStorage.setItem('rv_token', t)
    sessionStorage.setItem('rv_username', user)
    setToken(t)
    setUsername(user)
    posthog.identify(user, { name: user })
    posthog.capture('logged_in')
  }

  const handleLogout = () => {
    sessionStorage.removeItem('rv_token')
    sessionStorage.removeItem('rv_username')
    setToken(null)
    setUsername('')
    setSelectedAgent(null)
    posthog.reset()
  }

  const handleBack = () => setSelectedAgent(null)

  const handleSelectAgent = (agentId: string) => {
    posthog.capture('tool_opened', { tool: agentId })
    setSelectedAgent(agentId)
  }

  if (!token) return <LoginPage onLogin={handleLogin} />
  if (!selectedAgent) return <AgentSelectPage onSelect={handleSelectAgent} onLogout={handleLogout} />

  if (selectedAgent === 'fund-docs') {
    return <LPChatPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

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

  if (selectedAgent === 'fund-data') {
    return <FundDocsPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

if (selectedAgent === 'submit-deal') {
    return <SubmitDealPage token={token} onLogout={handleLogout} onBack={handleBack} />
  }

  return <ChatPage token={token} onLogout={handleLogout} onBack={handleBack} />
}
