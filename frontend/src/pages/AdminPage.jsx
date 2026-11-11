import { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { Brand } from '../components/Brand'
import { getAdminAlerts, getAdminSensors, getCurrentUser } from '../config/api'

export function AdminPage() {
  const navigate = useNavigate()
  const [devices, setDevices] = useState([])
  const [alerts, setAlerts] = useState([])
  const [notice, setNotice] = useState('')

  async function loadData() {
    const [sensorResponse, alertResponse] = await Promise.all([getAdminSensors(), getAdminAlerts()])
    setDevices(sensorResponse.items.map((sensor) => ({
      id: sensor.id,
      name: sensor.name,
      mqttUsername: sensor.mqtt_username,
      status: sensor.last_state || 'unknown',
      lastSeen: sensor.last_seen_at ? new Date(sensor.last_seen_at).toLocaleString() : 'nunca',
    })))
    setAlerts(alertResponse.items.map((alert) => ({
      id: alert.id,
      type: alert.alert_type,
      device: `Sensor #${alert.sensor_id}`,
      time: new Date(alert.occurred_at).toLocaleString(),
    })))
  }

  useEffect(() => {
    getCurrentUser().then((user) => {
      if (!user.admin) navigate('/home', { replace: true })
      else loadData().catch((error) => setNotice(error.message))
    }).catch(() => navigate('/login', { replace: true }))
  }, [navigate])

  const onlineDevices = devices.filter((device) => device.status === 'online').length

  function logout() {
    localStorage.removeItem('sentinela-auth')
    navigate('/login')
  }

  function exportReport() {
    const rows = ['Dispositivo,Usuário MQTT,Status,Última leitura', ...devices.map((device) =>
      [device.name, device.mqttUsername, device.status, device.lastSeen].join(','))]
    const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'relatorio-sentinela.csv'
    link.click()
    URL.revokeObjectURL(url)
    setNotice('Relatório exportado com os dados atuais.')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand compact />
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <NavLink to="/admin" className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}>Administração</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span className="online-dot" /> Sistema operacional
          <button className="logout-button" onClick={logout}>Sair da conta</button>
        </div>
      </aside>

      <main className="home-content admin-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CONTROLE OPERACIONAL</p>
            <h1>Administração</h1>
          </div>
          <div className="user-chip"><span className="avatar">AD</span><span>Administrador</span></div>
        </header>

        <section className="admin-intro">
          <div>
            <p className="eyebrow light">CENTRAL SENTINELA</p>
            <h2>Visão operacional</h2>
            <p>Acompanhe a saúde da rede e trate ocorrências sem sair do painel.</p>
          </div>
          <div className="admin-actions">
            <button className="secondary-button" onClick={() => loadData().then(() => setNotice('Dados atualizados.')).catch((error) => setNotice(error.message))}>Atualizar dados</button>
            <button className="primary-button compact" onClick={exportReport}>Exportar relatório <span>↓</span></button>
          </div>
        </section>

        {notice && <div className="admin-notice" role="status">{notice}<button onClick={() => setNotice('')} aria-label="Fechar aviso">×</button></div>}

        <section className="admin-metric-grid" aria-label="Resumo operacional">
          <article className="admin-metric"><span className="admin-metric-icon green">✓</span><div><span>DISPOSITIVOS ONLINE</span><strong>{onlineDevices}<small> / {devices.length}</small></strong><p>Rede estável</p></div></article>
          <article className="admin-metric"><span className="admin-metric-icon coral">!</span><div><span>ALERTAS REGISTRADOS</span><strong>{alerts.length}</strong><p>Dados do backend</p></div></article>
        </section>

        <section className="admin-main-grid">
          <article className="surface-card admin-table-card">
            <div className="section-heading">
              <div><p className="eyebrow">INVENTÁRIO</p><h2>Dispositivos monitorados</h2></div>
              <span className="tag success">{onlineDevices} online</span>
            </div>
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead><tr><th>Dispositivo</th><th>Status</th><th>Última leitura</th></tr></thead>
                <tbody>{devices.map((device) => <tr key={device.id}>
                  <td><strong>{device.name}</strong><small>{device.id} · MQTT: {device.mqttUsername}</small></td>
                  <td><span className={`status-label ${device.status}`}><i />{device.status === 'online' ? 'Online' : device.status === 'offline' ? 'Offline' : 'Desconhecido'}</span></td>
                  <td className="muted-cell">{device.lastSeen}</td>
                </tr>)}</tbody>
              </table>
            </div>
          </article>

          <article className="surface-card admin-alerts-card">
            <div className="section-heading">
              <div><p className="eyebrow">CENTRO DE ALERTAS</p><h2>Ocorrências recentes</h2></div>
              <span className="alert-count">{alerts.length}</span>
            </div>
            <div className="admin-alert-list">{alerts.map((alert) => <div className="admin-alert" key={alert.id}>
              <span className="alert-severity warning">•</span>
              <div><strong>{alert.type}</strong><p>{alert.device} · {alert.time}</p></div>
            </div>)}</div>
            {!alerts.length && <p className="empty-state">Nenhuma ocorrência registrada.</p>}
          </article>
        </section>
      </main>
    </div>
  )
}
