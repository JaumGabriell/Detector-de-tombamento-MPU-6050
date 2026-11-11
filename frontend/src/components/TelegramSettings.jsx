import { useEffect, useRef, useState } from 'react'
import { getCurrentUser, updateChatId } from '../config/api'

export function TelegramSettings() {
  const [chatId, setChatId] = useState('')
  const [message, setMessage] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const hasInteracted = useRef(false)
  const configured = Boolean(chatId)

  useEffect(() => {
    getCurrentUser()
      .then((user) => {
        setChatId(user.chat_id || '')
        if (!hasInteracted.current) {
          setIsEditing(!user.chat_id)
        }
      })
      .catch(() => {})
  }, [])

  async function save() {
    setMessage('')
    setIsSaving(true)

    try {
      const normalizedChatId = chatId.trim()
      await updateChatId(normalizedChatId)
      setChatId(normalizedChatId)
      setIsEditing(false)
      setMessage('Configuração salva com sucesso.')
    } catch (error) {
      setMessage(error.message)
    } finally {
      setIsSaving(false)
    }
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
      <div className="telegram-form">
        <label>
          Chat ID do Telegram
          {isEditing ? (
            <input
              value={chatId}
              onChange={(event) => setChatId(event.target.value)}
              placeholder="Ex.: -1001234567890"
              autoFocus
            />
          ) : (
            <span className="telegram-chat-id">{chatId}</span>
          )}
        </label>
        {isEditing ? (
          <button className="primary-button compact" type="button" onClick={save} disabled={isSaving || !chatId.trim()}>
            {isSaving ? 'Salvando...' : 'Salvar configuração'} <span>→</span>
          </button>
        ) : (
          <button
            className="primary-button compact"
            type="button"
            onClick={() => {
              hasInteracted.current = true
              setIsEditing(true)
              setMessage('')
            }}
          >
            Editar <span>↗</span>
          </button>
        )}
      </div>
      <p className="form-message">{message}</p>
    </section>
  )
}
