#!/usr/bin/env python3
"""
TumbleGuard - Detector de Tombamento v2
Apenas leitura de sensores (MPU6050 + GPS) e publicação MQTT para HiveMQ Cloud.
O backend (no computador) processa alertas e envia notificações Telegram.
"""

import ssl
import json
import uuid
import time
import math
import serial
import pynmea2
import smbus
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from paho.mqtt.enums import CallbackAPIVersion

# ================= CONFIGURAÇÕES =================
# MPU6050
MPU_ADDR = 0x68
LIMITE_TOMBAMENTO = 45.0

# GPS
GPS_PORT = "/dev/ttyAMA0"
GPS_BAUDRATE = 9600

# MQTT HiveMQ Cloud
MQTT_HOST = "d14c5ec1398548eb87862658e91f32ff.s1.eu.hivemq.cloud"
MQTT_PORT = 8883  # TLS
MQTT_USERNAME = "raspberrycarrinho"
MQTT_PASSWORD = "12345678"

# Sensor ID (deve existir no banco do backend)
SENSOR_ID = 1

# Intervalo entre leituras (segundos)
INTERVALO_LEITURA = 0.5

# Cooldown entre alertas (segundos)
COOLDOWN_ALERTA = 60

# ================= VARIÁVEIS GLOBAIS =================
bus = None
gps_serial = None
mqtt_client = None
mqtt_connected = False

# Últimas coordenadas GPS conhecidas
ultima_latitude = None
ultima_longitude = None
ultimo_alerta = 0

# ================= FUNÇÕES MPU6050 =================
def inicializar_mpu6050():
    """Inicializa o sensor MPU6050 via I2C"""
    global bus
    try:
        bus = smbus.SMBus(1)
        bus.write_byte_data(MPU_ADDR, 0x6B, 0)  # Acorda o sensor
        print("✅ MPU6050 inicializado")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar MPU6050: {e}")
        return False

def read_word(reg):
    """Lê um valor de 16 bits do sensor"""
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def ler_acelerometro():
    """Lê os valores do acelerômetro"""
    raw_x = read_word(0x3B)
    raw_y = read_word(0x3D)
    raw_z = read_word(0x3F)
    
    # Converte para g (±2g → 16384)
    x = raw_x / 16384.0
    y = raw_y / 16384.0
    z = raw_z / 16384.0
    
    return x, y, z

def calcular_inclinacao(x, y, z):
    """Calcula a inclinação em graus"""
    horizontal = math.sqrt(x*x + y*y)
    radianos = math.atan2(horizontal, z)
    graus = math.degrees(radianos)
    return abs(graus)

# ================= FUNÇÕES GPS =================
def inicializar_gps():
    """Inicializa a leitura do GPS via serial"""
    global gps_serial
    try:
        gps_serial = serial.Serial(GPS_PORT, GPS_BAUDRATE, timeout=1)
        print("✅ GPS inicializado")
        return True
    except Exception as e:
        print(f"⚠️  GPS não disponível: {e}")
        return False

def ler_gps():
    """Lê e parseia dados do GPS, retorna (latitude, longitude) ou (None, None)"""
    global ultima_latitude, ultima_longitude, gps_serial
    
    if not gps_serial:
        return ultima_latitude, ultima_longitude
    
    try:
        linha = gps_serial.readline().decode('ascii', errors='replace').strip()
        if linha.startswith('$GPGGA') or linha.startswith('$GPRMC'):
            msg = pynmea2.parse(linha)
            if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                if msg.latitude != 0.0 and msg.longitude != 0.0:
                    ultima_latitude = msg.latitude
                    ultima_longitude = msg.longitude
    except:
        pass
    
    return ultima_latitude, ultima_longitude

# ================= FUNÇÕES MQTT =================
def on_connect(client, userdata, flags, reason_code, properties):
    """Callback quando conecta ao HiveMQ"""
    global mqtt_connected
    if reason_code == 0:
        print("✅ Conectado ao HiveMQ Cloud")
        mqtt_connected = True
    else:
        print(f"❌ Falha na conexão MQTT: {reason_code}")
        mqtt_connected = False

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    """Callback quando desconecta"""
    global mqtt_connected
    mqtt_connected = False
    print(f"⚠️  Desconectado do MQTT: {reason_code}")

def inicializar_mqtt():
    """Inicializa conexão MQTT com HiveMQ Cloud"""
    global mqtt_client
    
    client_id = f"detector-{uuid.uuid4().hex[:8]}"
    
    mqtt_client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id=client_id,
        protocol=mqtt.MQTTv5
    )
    
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    
    print(f"📡 Conectando ao MQTT: {MQTT_HOST}:{MQTT_PORT} (TLS)")
    
    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar MQTT: {e}")
        return False

def publicar_telemetria(x, y, z, inclinacao, lat, lon):
    """Publica dados de telemetria via MQTT"""
    if not mqtt_connected:
        return
    
    payload = {
        "schema_version": 1,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(z, 3),
        "inclination": round(inclinacao, 2),
        "latitude": lat,
        "longitude": lon
    }
    
    topic = f"iot/v1/sensors/{SENSOR_ID}/telemetry"
    mqtt_client.publish(topic, json.dumps(payload), qos=0)

def publicar_alerta(x, y, z, inclinacao, lat, lon):
    """Publica alerta de tombamento via MQTT"""
    if not mqtt_connected:
        print("⚠️  MQTT desconectado, alerta não enviado")
        return False
    
    payload = {
        "schema_version": 1,
        "event_id": str(uuid.uuid4()),
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "type": "fall_detected",
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(z, 3),
        "inclination": round(inclinacao, 2),
        "latitude": lat,
        "longitude": lon
    }
    
    topic = f"iot/v1/sensors/{SENSOR_ID}/alerts"
    result = mqtt_client.publish(topic, json.dumps(payload), qos=1)
    
    try:
        result.wait_for_publish(timeout=5)
        print(f"🚨 Alerta publicado! Inclinação: {inclinacao:.1f}°")
        return True
    except:
        print("❌ Timeout ao publicar alerta")
        return False

# ================= LOOP PRINCIPAL =================
def main():
    global ultimo_alerta
    
    print("=" * 50)
    print("   🛡️  TumbleGuard - Detector de Tombamento")
    print("=" * 50)
    print(f"   Sensor ID: {SENSOR_ID}")
    print(f"   Limite: {LIMITE_TOMBAMENTO}°")
    print(f"   MQTT: {MQTT_HOST}:{MQTT_PORT}")
    print("=" * 50)
    
    # Inicializa sensores
    if not inicializar_mpu6050():
        print("❌ Não foi possível inicializar o MPU6050. Encerrando.")
        return
    
    inicializar_gps()
    
    # Inicializa MQTT
    if not inicializar_mqtt():
        print("❌ Não foi possível conectar ao MQTT. Encerrando.")
        return
    
    # Aguarda conexão
    time.sleep(2)
    
    if not mqtt_connected:
        print("❌ MQTT não conectou. Encerrando.")
        return
    
    print("\n📊 Iniciando monitoramento...\n")
    
    try:
        while True:
            # Lê sensores
            x, y, z = ler_acelerometro()
            inclinacao = calcular_inclinacao(x, y, z)
            lat, lon = ler_gps()
            
            # Status
            tombado = inclinacao > LIMITE_TOMBAMENTO
            status = "🔴 TOMBADO!" if tombado else "🟢 Normal"
            
            # GPS string
            if lat and lon:
                gps_str = f"({lat:.6f}, {lon:.6f})"
            else:
                gps_str = "(sem sinal)"
            
            # Print
            print(f"\r📐 Inclinação: {inclinacao:6.2f}° | 📍 GPS: {gps_str:30} | {status}", end="")
            
            # Publica telemetria
            publicar_telemetria(x, y, z, inclinacao, lat, lon)
            
            # Verifica tombamento
            if tombado:
                tempo_atual = time.time()
                if tempo_atual - ultimo_alerta > COOLDOWN_ALERTA:
                    print()  # Nova linha
                    print("🚨 TOMBAMENTO DETECTADO!")
                    if publicar_alerta(x, y, z, inclinacao, lat, lon):
                        ultimo_alerta = tempo_atual
            
            time.sleep(INTERVALO_LEITURA)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Encerrando...")
    
    finally:
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        if gps_serial:
            gps_serial.close()
        print("👋 Desconectado")

if __name__ == "__main__":
    main()
