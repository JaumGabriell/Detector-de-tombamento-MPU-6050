import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { login } from '../config/api'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [showPassword, setShowPassword] = useState(false)
  const [message, setMessage] = useState(location.state?.message || '')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function enterHome(event) {
    event.preventDefault()
    setMessage('')
    setIsSubmitting(true)
    localStorage.removeItem('sentinela-auth')
    const formData = new FormData(event.currentTarget)

    try {
      await login(formData.get('email'), formData.get('password'))
      navigate('/home', { replace: true })
    } catch (error) {
      setMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-intro">
        <div className="brand-mark">S</div>
        <p className="eyebrow">SENTINELA / IoT</p>
        <h1>Monitore o que mantém sua operação em movimento.</h1>
        <p className="intro-copy">
          Acompanhe o carrinho em tempo real e receba alertas de tombamento no Telegram.
        </p>
        <div className="intro-stat">
          <strong>24/7</strong>
          <span>proteção ativa para seus equipamentos</span>
        </div>
      </section>
      <section className="login-panel">
        <div className="panel-heading">
          <p className="eyebrow">ACESSO RESTRITO</p>
          <h2>Entrar na central</h2>
          <p>Use suas credenciais para continuar.</p>
        </div>
        <form className="form-stack" onSubmit={enterHome}>
          <label>
            E-mail
            <input name="email" type="email" placeholder="voce@empresa.com" required />
          </label>
          <label>
            Senha
            <div className="input-with-action">
              <input
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Digite sua senha"
                required
                minLength="4"
              />
              <button type="button" onClick={() => setShowPassword(!showPassword)}>
                {showPassword ? 'Ocultar' : 'Ver'}
              </button>
            </div>
          </label>
          <div className="form-options">
            <label className="checkbox-label">
              <input type="checkbox" /> Lembrar de mim
            </label>
            <button
              type="button"
              className="text-button"
              onClick={() => setMessage('Entre em contato com o administrador do sistema.')}
            >
              Esqueci minha senha
            </button>
          </div>
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Entrando...' : 'Entrar na central'} <span>→</span>
          </button>
          <p className="form-message">{message}</p>
          <p className="auth-switch">
            Ainda não possui uma conta? <Link to="/register">Criar cadastro</Link>
          </p>
        </form>
      </section>
    </main>
  )
}
