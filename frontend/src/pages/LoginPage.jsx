import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export function LoginPage() {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [message, setMessage] = useState('')

  function enterHome(event) {
    event.preventDefault()
    localStorage.setItem('sentinela-auth', 'true')
    navigate('/home')
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
          <button className="primary-button" type="submit">
            Entrar na central <span>→</span>
          </button>
          <p className="form-message">{message}</p>
        </form>
      </section>
    </main>
  )
}
