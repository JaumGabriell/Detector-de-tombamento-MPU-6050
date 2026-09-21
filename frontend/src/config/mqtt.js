const brokerUrl = import.meta.env.VITE_MQTT_BROKER || 'ws://192.168.4.1:9001/mqtt'
const url = new URL(brokerUrl)

export const MQTT_CONFIG = {
  broker: url.hostname,
  port: Number(url.port) || 9001,
  topic: 'carrinho/telemetria',
}