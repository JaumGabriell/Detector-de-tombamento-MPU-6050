import { useState } from 'react'

export function TelegramSettings() {
  const saved = JSON.parse(localStorage.getItem('sentinela-telegram') || '{}')
  const [chatId, setChatId] = useState(saved.chatId || '')
  const [message, setMessage] = useState('')
  const configured = Boolean(chatId)

  function save(event) {
    event.preventDefault()
    localStorage.setItem('sentinela-telegram', JSON.stringify({ chatId }))
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
          Chat ID do Telegram
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
