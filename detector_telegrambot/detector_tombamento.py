#!/usr/bin/env python3

import requests
import smbus
import time
import math
import json
import os
import threading
import paho.mqtt.client as mqtt

# ================= CONFIGURAÇÕES =================
MPU_ADDR = 0x68
LIMITE_TOMBAMENTO = 45.0
CONFIG_FILE = 'config.json'

# MQTT Config
MQTT_BROKER = "localhost"  # Broker local na Raspberry
MQTT_PORT = 1883
MQTT_TOPIC_CONFIG = "carrinho/config"  # Tópico para receber configurações
MQTT_TOPIC_TELEMETRIA = "carrinho/telemetria"  # Tópico para enviar dados

# API Config
API_URL = "http://localhost:8000"  # URL do backend FastAPI

# Função para carregar configuração
def carregar_config():
    """Carrega token e chat_id do arquivo config.json"""
    if not os.path.exists(CONFIG_FILE):
        print("⚠️  Arquivo config.json não encontrado!")
        print("   Configure o Telegram pelo app primeiro.")
        return None, None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        token = config.get('token')
        chat_id = config.get('chat_id')
        
        if not token or not chat_id:
            print("⚠️  Configuração incompleta no config.json")
            return None, None
        
        print(f"✅ Configuração carregada:")
        print(f"   Token: {token[:10]}...")
        print(f"   Chat ID: {chat_id}")
        return token, chat_id
    
    except Exception as e:
        print(f"❌ Erro ao ler config.json: {e}")
        return None, None

# Variáveis globais
token = None
chat_id = None
url = None
bus = None
mqtt_client = None
config_lock = threading.Lock()

# ================= FUNÇÕES =================
def read_word(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) + low
    
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    
    return value

def ler_acelerometro():
    raw_x = read_word(0x3B)
    raw_y = read_word(0x3D)
    raw_z = read_word(0x3F)

    # Converte para g (±2g → 16384)
    x = raw_x / 16384.0
    y = raw_y / 16384.0
    z = raw_z / 16384.0

    return x, y, z

def calcular_inclinacao(x, y, z):
    horizontal = math.sqrt(x*x + y*y)
    radianos = math.atan2(horizontal, z)
    graus = math.degrees(radianos)
    return graus

def buscar_chat_ids_do_backend():
    """Busca todos os chat_ids cadastrados no backend"""
    try:
        response = requests.get(f"{API_URL}/auth/users/chat-ids", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("chat_ids", [])
    except Exception as e:
        print(f"   ⚠️  Erro ao buscar chat_ids do backend: {e}")
    return []

def enviar_alerta_telegram():
    """Envia alerta de tombamento para o usuário configurado"""
    global token, chat_id, url
    
    # Recarrega configuração (caso tenha sido atualizada via MQTT)
    token, chat_id = carregar_config()
    
    if not token or not chat_id:
        print("   ⚠️  Telegram não configurado. Alerta não enviado.")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        mensagem = "🚨 ALERTA DE EMERGÊNCIA! 🚨\n\n"
        mensagem += "⚠️ TOMBAMENTO DETECTADO!\n\n"
        mensagem += f"🕒 Horário: {time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        mensagem += "📍 Localização: Raspberry Pi - TumbleGuard\n\n"
        mensagem += "Por favor, verifique imediatamente!"
        
        response = requests.post(
            url, 
            data={"chat_id": chat_id, "text": mensagem},
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Alerta enviado ao Telegram com sucesso!")
            return True
        else:
            print(f"   ❌ Erro ao enviar: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"   ❌ Erro ao enviar alerta: {e}")
        return False

# ================= MQTT CALLBACKS =================
def on_mqtt_connect(client, userdata, flags, rc):
    """Callback quando conecta ao broker MQTT"""
    if rc == 0:
        print("✅ Conectado ao broker MQTT")
        client.subscribe(MQTT_TOPIC_CONFIG)
        print(f"📡 Escutando configurações em: {MQTT_TOPIC_CONFIG}")
    else:
        print(f"❌ Falha ao conectar ao MQTT. Código: {rc}")

def on_mqtt_message(client, userdata, msg):
    """Callback quando recebe mensagem MQTT"""
    global token, chat_id, url
    
    try:
        payload = json.loads(msg.payload.decode())
        print(f"\n📨 Configuração recebida via MQTT:")
        
        novo_token = payload.get('token')
        novo_chat_id = payload.get('chat_id')
        
        if novo_token and novo_chat_id:
            with config_lock:
                # Salva no arquivo config.json
                config = {
                    'token': novo_token,
                    'chat_id': str(novo_chat_id)
                }
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Atualiza variáveis globais
                token = novo_token
                chat_id = str(novo_chat_id)
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                
            print(f"   ✅ Token: {token[:10]}...")
            print(f"   ✅ Chat ID: {chat_id}")
            print(f"   ✅ Configuração salva em {CONFIG_FILE}\n")
            
            # Envia confirmação de volta via MQTT
            confirmacao = {
                'status': 'success',
                'message': 'Configuração salva com sucesso!',
                'chat_id': chat_id
            }
            client.publish("carrinho/config/response", json.dumps(confirmacao))
        else:
            print("   ⚠️  Dados incompletos (token ou chat_id ausente)")
            
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar JSON: {msg.payload}")
    except Exception as e:
        print(f"❌ Erro ao processar configuração: {e}")

def iniciar_mqtt():
    """Inicia o cliente MQTT em uma thread separada"""
    global mqtt_client
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()  # Inicia loop em thread separada
        print(f"🔌 Conectando ao broker MQTT ({MQTT_BROKER}:{MQTT_PORT})...")
    except Exception as e:
        print(f"⚠️  Não foi possível conectar ao MQTT: {e}")
        print("   O sistema continuará funcionando sem MQTT")

def publicar_telemetria(x, y, z, inclinacao, status):
    """Publica dados de telemetria via MQTT"""
    global mqtt_client
    
    if mqtt_client and mqtt_client.is_connected():
        dados = {
            'acelerometro': {'x': round(x, 2), 'y': round(y, 2), 'z': round(z, 2)},
            'inclinacao': round(inclinacao, 2),
            'alerta': 'TOMBAMENTO DETECTADO!' if inclinacao > LIMITE_TOMBAMENTO else 'OK',
            'timestamp': time.time()
        }
        mqtt_client.publish(MQTT_TOPIC_TELEMETRIA, json.dumps(dados))

# ================= LOOP PRINCIPAL =================
def main():
    """Função principal do detector"""
    global token, chat_id, url, bus
    
    # Inicia cliente MQTT
    iniciar_mqtt()
    time.sleep(1)  # Aguarda conexão MQTT
    
    # Carrega configuração inicial
    token, chat_id = carregar_config()

    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
    else:
        url = None
        print("⚠️  Sistema rodando SEM notificações do Telegram")
        print("   Configure via MQTT ou crie o arquivo config.json")

    # Inicializa I2C
    bus = smbus.SMBus(1)

    # Acorda o MPU6050
    bus.write_byte_data(MPU_ADDR, 0x6B, 0)
    
    print("🚗 Sistema de Detecção de Tombamento (MPU6050)")
    print("Pressione Ctrl+C para sair\n")

    contador = 0
    ultimo_alerta = 0  # Evita spam de alertas

    try:
        while True:
            contador += 1

            x, y, z = ler_acelerometro()
            inclinacao = calcular_inclinacao(x, y, z)

            # Verifica tombamento
            if inclinacao > LIMITE_TOMBAMENTO:
                status = "🚨 TOMBADO"
            else:
                status = "✅ OK"

            # Print formatado
            print(f"[{contador:04d}] X={x:.2f} Y={y:.2f} Z={z:.2f} | {status}, {inclinacao:.2f}°")
            
            # Publica telemetria via MQTT
            publicar_telemetria(x, y, z, inclinacao, status)

            # Envia alerta apenas uma vez a cada 60 segundos
            if inclinacao > LIMITE_TOMBAMENTO:
                tempo_atual = time.time()
                if tempo_atual - ultimo_alerta > 60:  # 60 segundos de cooldown
                    print("⚠️  🚨 TOMBAMENTO DETECTADO! Enviando alerta...\n")
                    if enviar_alerta_telegram():
                        ultimo_alerta = tempo_atual

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️ Encerrado pelo usuário")
    finally:
        # Encerra cliente MQTT
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("🔌 MQTT desconectado")

if __name__ == '__main__':
    main()
