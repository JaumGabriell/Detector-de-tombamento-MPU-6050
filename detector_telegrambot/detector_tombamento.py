#!/usr/bin/env python3

import requests
import smbus
import time
import math
import json
import os

# ================= CONFIGURAÇÕES =================
MPU_ADDR = 0x68
LIMITE_TOMBAMENTO = 45.0
CONFIG_FILE = 'config.json'

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

def enviar_alerta_telegram():
    """Envia alerta de tombamento para o Telegram"""
    global token, chat_id, url
    
    # Recarrega configuração (caso tenha sido atualizada)
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

# ================= LOOP PRINCIPAL =================
def main():
    """Função principal do detector"""
    global token, chat_id, url, bus
    
    # Carrega configuração inicial
    token, chat_id = carregar_config()

    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
    else:
        url = None
        print("⚠️  Sistema rodando SEM notificações do Telegram")

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

if __name__ == '__main__':
    main()
