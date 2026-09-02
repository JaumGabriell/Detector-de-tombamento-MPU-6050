import { useState } from 'react'

export function TelegramSettings() {
  const saved = JSON.parse(localStorage.getItem('sentinela-telegram') || '{}')
  const [token, setToken] = useState(saved.token || '')
  const [chatId, setChatId] = useState(saved.chatId || '')
  const [message, setMessage] = useState('')
  const configured = Boolean(token && chatId)

  function save(event) {
    event.preventDefault()
    localStorage.setItem('sentinela-telegram', JSON.stringify({ token, chatId }))
    setMessage('Configuração salva neste navegador.')
  }

  return (
    <section className="surface-card telegram-card" id="telegram">
      <div className="section-heading">
        <div>
          <p className="eyebrow">NOTIFICAÇÕES</p>
          <h2>Configuração do Telegram</h2>
          <p>Receba alertas automaticamente quando um tombamento for detectado.</p>
        </div>
        <span className={`tag ${configured ? 'success' : ''}`}>
          {configured ? 'Configurado' : 'Não configurado'}
        </span>
      </div>
      <form className="telegram-form" onSubmit={save}>
        <label>
          Bot Token
          <input
            type="password"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            placeholder="Cole o token do seu bot"
          />
        </label>
        <label>
          Chat ID
          <input
            value={chatId}
            onChange={(event) => setChatId(event.target.value)}
            placeholder="Ex.: -1001234567890"
          />
        </label>
        <button className="primary-button compact" type="submit">
          Salvar configuração <span>→</span>
        </button>
      </form>
      <p className="form-message">{message}</p>
    </section>
  )
}
