import { NavLink, useNavigate } from 'react-router-dom'
import { Brand } from '../components/Brand'
import { getCurrentUser } from '../config/api'
import { useEffect, useState } from 'react'

const STATIC_LOCATION = {
  latitude: '-22.4256',
  longitude: '-45.4528',
  address: 'Santa Rita do Sapucaí, MG',
  updatedAt: 'Agora mesmo',
}

export function GpsPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((error) => {
        if (error.status === 401) {
          localStorage.removeItem('sentinela-auth')
          navigate('/login', { replace: true })
        }
      })
  }, [navigate])

  function logout() {
    localStorage.removeItem('sentinela-auth')
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand compact />
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <NavLink to="/home" className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}>
            Início
          </NavLink>
          <NavLink to="/gps" className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}>
            Visualizar GPS
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <span className="online-dot" /> Sistema operacional
          <button className="logout-button" onClick={logout}>Sair da conta</button>
        </div>
      </aside>
      <main className="home-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CENTRAL DE MONITORAMENTO</p>
            <h1>Localização</h1>
          </div>
          <div className="user-chip"><span className="avatar">{user?.name?.slice(0, 2).toUpperCase() || 'AC'}</span><span>{user?.name || 'Carregando...'}</span></div>
        </header>
        <section className="hero-banner">
          <div>
            <p className="eyebrow light">RASTREAMENTO DO DISPOSITIVO</p>
            <h2>Carrinho IoT 01</h2>
            <p>Visualização de localização em modo demonstração.</p>
          </div>
          <div className="system-status"><span className="pulse-dot" /><strong>Posição simulada</strong></div>
        </section>
        <section className="gps-layout">
          <article className="surface-card static-map">
            <div className="map-grid" />
            <div className="map-pin">●</div>
            <span className="map-label">Carrinho IoT 01</span>
            <span className="map-road road-one" />
            <span className="map-road road-two" />
          </article>
          <article className="surface-card location-card">
            <p className="eyebrow">DISPOSITIVO ATIVO</p>
            <h2>Localização atual</h2>
            <div className="location-status"><span className="pulse-dot" /> Posição disponível</div>
            <dl className="location-details">
              <div><dt>Local aproximado</dt><dd>{STATIC_LOCATION.address}</dd></div>
              <div><dt>Latitude</dt><dd>{STATIC_LOCATION.latitude}</dd></div>
              <div><dt>Longitude</dt><dd>{STATIC_LOCATION.longitude}</dd></div>
              <div><dt>Última atualização</dt><dd>{STATIC_LOCATION.updatedAt}</dd></div>
            </dl>
            <p className="card-footnote">Coordenadas fixas para demonstração. A integração com GPS será conectada posteriormente.</p>
          </article>
        </section>
      </main>
    </div>
  )
}