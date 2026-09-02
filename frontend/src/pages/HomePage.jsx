import { useNavigate } from 'react-router-dom'
import { Brand } from '../components/Brand'
import { MetricCard } from '../components/MetricCard'
import { TelegramSettings } from '../components/TelegramSettings'
import { MQTT_CONFIG } from '../config/mqtt'
import { useMqttTelemetry } from '../hooks/useMqttTelemetry'

export function HomePage() {
  const navigate = useNavigate()
  const { telemetry, connection } = useMqttTelemetry()
  const isConnected = connection === 'Conectado'

  function logout() {
    localStorage.removeItem('sentinela-auth')
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand compact />
        <div className="sidebar-footer">
          <span className="online-dot" /> Sistema operacional
          <button className="logout-button" onClick={logout}>Sair da conta</button>
        </div>
      </aside>
      <main className="home-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CENTRAL DE MONITORAMENTO</p>
            <h1>Visão geral</h1>
          </div>
          <div className="user-chip"><span className="avatar">AC</span><span>Administrador</span></div>
        </header>
        <section className="hero-banner">
          <div>
            <p className="eyebrow light">STATUS DO SISTEMA</p>
            <h2>Monitor de tombamento</h2>
            <p>Seu carrinho está sendo acompanhado em tempo real.</p>
          </div>
          <div className="system-status">
            <span className="pulse-dot" />
            <strong>{isConnected ? 'Operacional' : connection}</strong>
            <span>{telemetry.lastUpdate}</span>
          </div>
        </section>
        <section className="metric-grid">
          <MetricCard label="ACELERÔMETRO X" value={telemetry.x} color="red" note="Eixo esquerda / direita" />
          <MetricCard label="ACELERÔMETRO Y" value={telemetry.y} color="blue" note="Eixo frente / trás" />
          <MetricCard label="ACELERÔMETRO Z" value={telemetry.z} color="green" note="Eixo cima / baixo" />
          <MetricCard label="INCLINAÇÃO TOTAL" value={telemetry.angle} color="amber" note="Dentro do limite seguro" />
        </section>
        <section className="content-grid">
          <article className="surface-card device-card" id="dispositivo">
            <div className="section-heading">
              <div><p className="eyebrow">DISPOSITIVO ATIVO</p><h2>Carrinho IoT 01</h2></div>
              <span className={`tag ${isConnected ? 'success' : ''}`}>{isConnected ? 'Conectado' : 'Aguardando'}</span>
            </div>
            <div className="device-visual">
              <div className="cart-icon">▰</div>
              <div><strong>{telemetry.fallen ? 'Tombamento detectado' : 'Sem alertas detectados'}</strong><p>Última leitura recebida às {telemetry.lastUpdate}</p></div>
            </div>
            <div className="device-meta">
              <span><small>Broker MQTT</small>{MQTT_CONFIG.broker}:{MQTT_CONFIG.port}</span>
              <span><small>Tópico</small>{MQTT_CONFIG.topic}</span>
              <span><small>Latência</small>42 ms</span>
            </div>
          </article>
          <article className="surface-card alert-card">
            <div className="section-heading">
              <div><p className="eyebrow">ESTADO ATUAL</p><h2>Indicador visual</h2></div>
              <span className={`alert-icon ${telemetry.fallen ? 'fallen' : ''}`}>{telemetry.fallen ? '!' : '✓'}</span>
            </div>
            <div className={`visual-indicator ${telemetry.fallen ? 'fallen' : ''}`}>
              <span>{telemetry.fallen ? 'Tombado' : 'Seguro'}</span><strong>{telemetry.fallen ? '!' : '0'}</strong>
            </div>
            <p className="card-footnote">{telemetry.fallen ? 'Verifique o dispositivo imediatamente.' : 'Nenhuma ocorrência nas últimas 24 horas.'}</p>
          </article>
        </section>
        <TelegramSettings />
      </main>
    </div>
  )
}
