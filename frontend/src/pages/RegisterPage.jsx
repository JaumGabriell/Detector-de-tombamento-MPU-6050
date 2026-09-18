import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../config/api'

export function RegisterPage() {
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function createAccount(event) {
    event.preventDefault()
    setMessage('')
    const formData = new FormData(event.currentTarget)
    const password = formData.get('password')

    if (password !== formData.get('passwordConfirmation')) {
      setMessage('As senhas precisam ser iguais.')
      return
    }

    setIsSubmitting(true)
    try {
      await register(formData.get('name'), formData.get('email'), password)
      navigate('/login', { state: { message: 'Conta criada. Entre com suas credenciais.' } })
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
        <h1>Crie seu acesso à central de monitoramento.</h1>
        <p className="intro-copy">
          Configure sua conta para acompanhar o carrinho e receber alertas de tombamento.
        </p>
        <div className="intro-stat">
          <strong>24/7</strong>
          <span>visibilidade sobre seus equipamentos</span>
        </div>
      </section>
      <section className="login-panel">
        <div className="panel-heading">
          <p className="eyebrow">NOVO ACESSO</p>
          <h2>Criar conta</h2>
          <p>Preencha seus dados para começar.</p>
        </div>
        <form className="form-stack" onSubmit={createAccount}>
          <label>
            Nome completo
            <input name="name" type="text" placeholder="Maria Silva" required maxLength="100" />
          </label>
          <label>
            E-mail
            <input name="email" type="email" placeholder="voce@empresa.com" required />
          </label>
          <label>
            Senha
            <input name="password" type="password" placeholder="Mínimo de 8 caracteres" required minLength="8" />
          </label>
          <label>
            Confirmar senha
            <input name="passwordConfirmation" type="password" placeholder="Repita sua senha" required minLength="8" />
          </label>
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Criando conta...' : 'Criar minha conta'} <span>→</span>
          </button>
          <p className="form-message">{message}</p>
          <p className="auth-switch">
            Já possui uma conta? <Link to="/login">Entrar na central</Link>
          </p>
        </form>
      </section>
    </main>
  )
}