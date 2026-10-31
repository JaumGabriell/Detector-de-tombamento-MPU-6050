import { useMemo, useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { Brand } from '../components/Brand'

const initialDevices = [
  { id: 'IOT-01', name: 'Carrinho IoT 01', location: 'Laboratório de protótipos', status: 'online', battery: 92, lastSeen: 'agora' },
  { id: 'IOT-02', name: 'Carrinho IoT 02', location: 'Área externa', status: 'online', battery: 67, lastSeen: 'há 2 min' },
  { id: 'IOT-03', name: 'Carrinho IoT 03', location: 'Oficina mecânica', status: 'offline', battery: 18, lastSeen: 'há 28 min' },
]

const initialAlerts = [
  { id: 1, type: 'Tombamento', device: 'Carrinho IoT 02', time: 'Hoje, 14:32', severity: 'critical', acknowledged: false },
  { id: 2, type: 'Bateria baixa', device: 'Carrinho IoT 03', time: 'Hoje, 13:10', severity: 'warning', acknowledged: false },
  { id: 3, type: 'Sensor desconectado', device: 'Carrinho IoT 03', time: 'Hoje, 12:48', severity: 'warning', acknowledged: true },
]

export function AdminPage() {
  const navigate = useNavigate()
  const [devices, setDevices] = useState(initialDevices)
  const [alerts, setAlerts] = useState(initialAlerts)
  const [filter, setFilter] = useState('todos')
  const [maintenanceMode, setMaintenanceMode] = useState(false)
  const [notice, setNotice] = useState('')

  const visibleAlerts = useMemo(() => {
    if (filter === 'pendentes') return alerts.filter((alert) => !alert.acknowledged)
    if (filter === 'criticos') return alerts.filter((alert) => alert.severity === 'critical')
    return alerts
  }, [alerts, filter])

  const pendingAlerts = alerts.filter((alert) => !alert.acknowledged).length
  const onlineDevices = devices.filter((device) => device.status === 'online').length

  function logout() {
    localStorage.removeItem('sentinela-auth')
    navigate('/login')
  }

  function acknowledgeAlert(id) {
    setAlerts((current) => current.map((alert) => alert.id === id ? { ...alert, acknowledged: true } : alert))
    setNotice('Alerta marcado como revisado.')
  }

  function toggleMaintenance(deviceId) {
    setDevices((current) => current.map((device) => device.id === deviceId
      ? { ...device, status: device.status === 'maintenance' ? 'online' : 'maintenance' }
      : device))
    setNotice('Status do dispositivo atualizado localmente.')
  }

  function exportReport() {
    const rows = ['Dispositivo,Localização,Status,Bateria,Última leitura', ...devices.map((device) =>
      [device.name, device.location, device.status, `${device.battery}%`, device.lastSeen].join(','))]
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
          <NavLink to="/home" className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}>Início</NavLink>
          <NavLink to="/gps" className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}>Visualizar GPS</NavLink>
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
            <button className="secondary-button" onClick={() => setNotice('Dados atualizados localmente.')}>Atualizar dados</button>
            <button className="primary-button compact" onClick={exportReport}>Exportar relatório <span>↓</span></button>
          </div>
        </section>

        {notice && <div className="admin-notice" role="status">{notice}<button onClick={() => setNotice('')} aria-label="Fechar aviso">×</button></div>}

        <section className="admin-metric-grid" aria-label="Resumo operacional">
          <article className="admin-metric"><span className="admin-metric-icon green">✓</span><div><span>DISPOSITIVOS ONLINE</span><strong>{onlineDevices}<small> / {devices.length}</small></strong><p>Rede estável</p></div></article>
          <article className="admin-metric"><span className="admin-metric-icon coral">!</span><div><span>ALERTAS PENDENTES</span><strong>{pendingAlerts}</strong><p>{pendingAlerts ? 'Requer atenção' : 'Tudo em dia'}</p></div></article>
          <article className="admin-metric"><span className="admin-metric-icon amber">◷</span><div><span>UPTIME MÉDIO</span><strong>98,4%</strong><p>Últimos 30 dias</p></div></article>
          <article className="admin-metric"><span className="admin-metric-icon blue">↗</span><div><span>LEITURAS HOJE</span><strong>12.840</strong><p>+8,2% vs. ontem</p></div></article>
        </section>

        <section className="admin-main-grid">
          <article className="surface-card admin-table-card">
            <div className="section-heading">
              <div><p className="eyebrow">INVENTÁRIO</p><h2>Dispositivos monitorados</h2></div>
              <span className="tag success">{onlineDevices} online</span>
            </div>
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead><tr><th>Dispositivo</th><th>Status</th><th>Bateria</th><th>Última leitura</th><th /></tr></thead>
                <tbody>{devices.map((device) => <tr key={device.id}>
                  <td><strong>{device.name}</strong><small>{device.id} · {device.location}</small></td>
                  <td><span className={`status-label ${device.status}`}><i />{device.status === 'online' ? 'Online' : device.status === 'maintenance' ? 'Manutenção' : 'Offline'}</span></td>
                  <td><span className={`battery ${device.battery < 25 ? 'low' : ''}`}><i style={{ width: `${device.battery}%` }} />{device.battery}%</span></td>
                  <td className="muted-cell">{device.lastSeen}</td>
                  <td><button className="table-action" onClick={() => toggleMaintenance(device.id)}>{device.status === 'maintenance' ? 'Retomar' : 'Manutenção'}</button></td>
                </tr>)}</tbody>
              </table>
            </div>
          </article>

          <article className="surface-card admin-alerts-card">
            <div className="section-heading">
              <div><p className="eyebrow">CENTRO DE ALERTAS</p><h2>Ocorrências recentes</h2></div>
              <span className="alert-count">{pendingAlerts}</span>
            </div>
            <div className="alert-filters">
              {['todos', 'pendentes', 'criticos'].map((option) => <button key={option} className={filter === option ? 'selected' : ''} onClick={() => setFilter(option)}>{option === 'todos' ? 'Todos' : option === 'pendentes' ? 'Pendentes' : 'Críticos'}</button>)}
            </div>
            <div className="admin-alert-list">{visibleAlerts.map((alert) => <div className={`admin-alert ${alert.acknowledged ? 'acknowledged' : ''}`} key={alert.id}>
              <span className={`alert-severity ${alert.severity}`}>{alert.severity === 'critical' ? '!' : '•'}</span>
              <div><strong>{alert.type}</strong><p>{alert.device} · {alert.time}</p></div>
              {!alert.acknowledged && <button className="table-action" onClick={() => acknowledgeAlert(alert.id)}>Revisar</button>}
            </div>)}</div>
            {!visibleAlerts.length && <p className="empty-state">Nenhuma ocorrência nesta categoria.</p>}
          </article>
        </section>

        <section className="surface-card admin-preferences">
          <div><p className="eyebrow">PREFERÊNCIAS RÁPIDAS</p><h2>Modo de manutenção global</h2><p>Suspende notificações durante intervenções programadas.</p></div>
          <button className={`toggle ${maintenanceMode ? 'on' : ''}`} onClick={() => setMaintenanceMode((current) => !current)} aria-pressed={maintenanceMode}><span />{maintenanceMode ? 'Ativado' : 'Desativado'}</button>
        </section>
      </main>
    </div>
  )
}
