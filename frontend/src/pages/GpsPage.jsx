import { NavLink, useNavigate } from "react-router-dom";
import { Brand } from "../components/Brand";
import { getCurrentUser } from "../config/api";
import { useEffect, useState, useCallback, lazy, Suspense } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const SENSOR_ID = 1;

// Lazy load do componente de mapa
const MapComponent = lazy(() => import("../components/MapComponent"));

export function GpsPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [location, setLocation] = useState({
    latitude: null,
    longitude: null,
    lastUpdate: "Aguardando...",
    connected: false,
  });

  const getToken = () => {
    try {
      return JSON.parse(localStorage.getItem("sentinela-auth") || "null")
        ?.access_token;
    } catch {
      return null;
    }
  };

  const fetchLocation = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    try {
      const res = await fetch(`${API_URL}/sensor/${SENSOR_ID}/telemetry`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Erro ao buscar localização");

      const json = await res.json();

      if (json.connected && json.data) {
        const data = json.data;
        setLocation({
          latitude: data.latitude,
          longitude: data.longitude,
          lastUpdate: data.occurred_at
            ? new Date(data.occurred_at).toLocaleTimeString("pt-BR")
            : "Agora",
          connected: true,
        });
      } else {
        setLocation((prev) => ({
          ...prev,
          connected: false,
          lastUpdate: "Sensor offline",
        }));
      }
    } catch (e) {
      console.error("Erro ao buscar localização:", e);
    }
  }, []);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch((error) => {
        if (error.status === 401) {
          localStorage.removeItem("sentinela-auth");
          navigate("/login", { replace: true });
        }
      });
  }, [navigate]);

  useEffect(() => {
    fetchLocation();
    const interval = setInterval(fetchLocation, 1000);
    return () => clearInterval(interval);
  }, [fetchLocation]);

  function logout() {
    localStorage.removeItem("sentinela-auth");
    navigate("/login");
  }

  const hasPosition = location.latitude && location.longitude;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand compact />
        <nav className="sidebar-nav" aria-label="Navegação principal">
          <NavLink
            to="/home"
            className={({ isActive }) =>
              isActive ? "sidebar-link active" : "sidebar-link"
            }
          >
            Início
          </NavLink>
          <NavLink
            to="/gps"
            className={({ isActive }) =>
              isActive ? "sidebar-link active" : "sidebar-link"
            }
          >
            Visualizar GPS
          </NavLink>
        </nav>
        <div className="sidebar-footer">
          <span className="online-dot" /> Sistema operacional
          <button className="logout-button" onClick={logout}>
            Sair da conta
          </button>
        </div>
      </aside>
      <main className="home-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">CENTRAL DE MONITORAMENTO</p>
            <h1>Localização GPS</h1>
          </div>
          <div className="user-chip">
            <span className="avatar">
              {user?.name?.slice(0, 2).toUpperCase() || "AC"}
            </span>
            <span>{user?.name || "Carregando..."}</span>
          </div>
        </header>
        <section className="hero-banner">
          <div>
            <p className="eyebrow light">RASTREAMENTO EM TEMPO REAL</p>
            <h2>Carrinho IoT 01</h2>
            <p>Acompanhe a localização do dispositivo em tempo real.</p>
          </div>
          <div className="system-status">
            <span
              className={location.connected ? "pulse-dot" : "pulse-dot offline"}
            />
            <strong>
              {location.connected ? "GPS Conectado" : "Aguardando sinal"}
            </strong>
          </div>
        </section>
        <section className="gps-layout">
          <article
            className="surface-card"
            style={{ padding: 0, overflow: "hidden", minHeight: "400px" }}
          >
            <Suspense
              fallback={
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "400px",
                  }}
                >
                  Carregando mapa...
                </div>
              }
            >
              <MapComponent location={location} />
            </Suspense>
          </article>
          <article className="surface-card location-card">
            <p className="eyebrow">DISPOSITIVO ATIVO</p>
            <h2>Localização atual</h2>
            <div className="location-status">
              <span
                className={
                  location.connected ? "pulse-dot" : "pulse-dot offline"
                }
              />
              {location.connected ? "Posição disponível" : "Aguardando GPS"}
            </div>
            <dl className="location-details">
              <div>
                <dt>Latitude</dt>
                <dd>{location.latitude?.toFixed(6) || "—"}</dd>
              </div>
              <div>
                <dt>Longitude</dt>
                <dd>{location.longitude?.toFixed(6) || "—"}</dd>
              </div>
              <div>
                <dt>Última atualização</dt>
                <dd>{location.lastUpdate}</dd>
              </div>
            </dl>
            {hasPosition && (
              <a
                href={`https://www.google.com/maps?q=${location.latitude},${location.longitude}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary"
                style={{
                  display: "inline-block",
                  marginTop: "1rem",
                  textDecoration: "none",
                }}
              >
                Abrir no Google Maps
              </a>
            )}
          </article>
        </section>
      </main>
    </div>
  );
}
