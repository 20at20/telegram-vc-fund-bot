import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import ChatPage from './pages/ChatPage'

export default function App() {
  const [token, setToken] = useState<string | null>(
    sessionStorage.getItem('rv_token')
  )

  const handleLogin = (t: string) => {
    sessionStorage.setItem('rv_token', t)
    setToken(t)
  }

  const handleLogout = () => {
    sessionStorage.removeItem('rv_token')
    setToken(null)
  }

  return token
    ? <ChatPage token={token} onLogout={handleLogout} />
    : <LoginPage onLogin={handleLogin} />
}
