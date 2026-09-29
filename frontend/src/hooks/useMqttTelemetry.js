import { useEffect, useState, useCallback } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const SENSOR_ID = 1;
const POLL_INTERVAL = 500; // ms

const initialTelemetry = {
  x: "0.00",
  y: "0.00",
  z: "0.00",
  angle: "0.0°",
  fallen: false,
  lastUpdate: "Sem conexão",
  latitude: null,
  longitude: null,
};

export function useMqttTelemetry() {
  const [telemetry, setTelemetry] = useState(initialTelemetry);
  const [connection, setConnection] = useState("Conectando...");
  const [alerts, setAlerts] = useState([]);

  const getToken = () => {
    try {
      return JSON.parse(localStorage.getItem("sentinela-auth") || "null")
        ?.access_token;
    } catch {
      return null;
    }
  };

  const fetchTelemetry = useCallback(async () => {
    const token = getToken();
    if (!token) {
      setConnection("Não autenticado");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/sensor/${SENSOR_ID}/telemetry`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Erro ao buscar telemetria");

      const json = await res.json();

      if (json.connected && json.data) {
        const data = json.data;
        setTelemetry({
          x: data.x?.toFixed(2) || "0.00",
          y: data.y?.toFixed(2) || "0.00",
          z: data.z?.toFixed(2) || "0.00",
          angle: `${Number(data.inclination || 0).toFixed(1)}°`,
          fallen: (data.inclination || 0) > 45,
          lastUpdate: data.occurred_at
            ? new Date(data.occurred_at).toLocaleTimeString("pt-BR")
            : "Agora",
          latitude: data.latitude,
          longitude: data.longitude,
        });
        setConnection("Conectado");
      } else {
        setConnection("Sensor offline");
        setTelemetry(initialTelemetry);
      }
    } catch (e) {
      console.error("Erro ao buscar telemetria:", e);
      setConnection("Erro de conexão");
    }
  }, []);

  const fetchAlerts = useCallback(async () => {
    const token = getToken();
    if (!token) return;

    try {
      const res = await fetch(`${API_URL}/sensor/${SENSOR_ID}/alert?page=1`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error("Erro ao buscar alertas");

      const json = await res.json();

      setAlerts(
        json.items?.map((alert) => ({
          id: alert.event_id,
          type: alert.alert_type,
          inclination: alert.inclination,
          time: new Date(alert.occurred_at).toLocaleTimeString("pt-BR"),
        })) || [],
      );
    } catch (e) {
      console.error("Erro ao buscar alertas:", e);
    }
  }, []);

  useEffect(() => {
    // Busca inicial
    fetchTelemetry();
    fetchAlerts();

    // Polling de telemetria
    const telemetryInterval = setInterval(fetchTelemetry, POLL_INTERVAL);

    // Atualiza alertas a cada 5 segundos
    const alertsInterval = setInterval(fetchAlerts, 5000);

    return () => {
      clearInterval(telemetryInterval);
      clearInterval(alertsInterval);
    };
  }, [fetchTelemetry, fetchAlerts]);

  return { telemetry, connection, alerts };
}
