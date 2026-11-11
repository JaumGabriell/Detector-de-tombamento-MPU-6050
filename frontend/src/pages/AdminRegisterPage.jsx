import { useState } from 'react'
import { createAdminUser } from '../config/api'

export function AdminRegisterPage() {
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function submit(event) {
    event.preventDefault()
    const form = event.currentTarget
    const data = new FormData(form)
    if (data.get('password') !== data.get('confirmation')) {
      setMessage('As senhas precisam ser iguais.')
      return
    }

    setIsSubmitting(true)
    setMessage('')
    try {
      await createAdminUser({
        name: data.get('name'),
        email: data.get('email'),
        password: data.get('password'),
      })
      setMessage('Administrador cadastrado com sucesso.')
      form.reset()
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
        <p className="eyebrow">SENTINELA / ADMIN</p>
        <h1>Cadastre um novo administrador.</h1>
        <p className="intro-copy">Esta área é restrita a administradores autenticados.</p>
      </section>
      <section className="login-panel">
        <div className="panel-heading">
          <p className="eyebrow">ACESSO RESTRITO</p>
          <h2>Novo administrador</h2>
          <p>Crie as credenciais para acesso administrativo.</p>
        </div>
        <form className="form-stack" onSubmit={submit}>
          <label>Nome completo<input name="name" required maxLength="100" /></label>
          <label>E-mail<input name="email" type="email" required /></label>
          <label>Senha<input name="password" type="password" minLength="8" required /></label>
          <label>Confirmar senha<input name="confirmation" type="password" minLength="8" required /></label>
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Cadastrando...' : 'Cadastrar administrador'} <span>→</span>
          </button>
          <p className="form-message">{message}</p>
        </form>
      </section>
    </main>
  )
}
