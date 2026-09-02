import { useEffect, useState } from 'react'
import { Client } from 'paho-mqtt'
import { MQTT_CONFIG } from '../config/mqtt'

const initialTelemetry = {
  x: '0.02',
  y: '-0.01',
  z: '9.81',
  angle: '1.2°',
  fallen: false,
  lastUpdate: 'Sem dados',
}

export function useMqttTelemetry() {
  const [telemetry, setTelemetry] = useState(initialTelemetry)
  const [connection, setConnection] = useState('Conectando ao broker MQTT...')

  useEffect(() => {
    const client = new Client(
      MQTT_CONFIG.broker,
      MQTT_CONFIG.port,
      '/mqtt',
      `dashboard_${Math.random().toString(16).slice(2, 10)}`,
    )

    client.onConnectionLost = () => setConnection('Desconectado')
    client.onMessageArrived = (message) => {
      try {
        const data = JSON.parse(message.payloadString)
        if (!data.acelerometro || !data.timestamp) return

        setTelemetry({
          x: data.acelerometro.x,
          y: data.acelerometro.y,
          z: data.acelerometro.z,
          angle: `${Number(data.inclinacao).toFixed(1)}°`,
          fallen: Boolean(data.alerta?.includes('TOMBAMENTO')),
          lastUpdate: new Date(data.timestamp * 1000).toLocaleTimeString('pt-BR'),
        })
      } catch {
        // Mensagens MQTT inválidas não devem interromper o monitoramento.
      }
    }

    client.connect({
      timeout: 10,
      useSSL: false,
      onSuccess: () => {
        setConnection('Conectado')
        client.subscribe(MQTT_CONFIG.topic)
      },
      onFailure: () => setConnection('Sem conexão'),
    })

    return () => {
      if (client.isConnected()) client.disconnect()
    }
  }, [])

  return { telemetry, connection }
}
