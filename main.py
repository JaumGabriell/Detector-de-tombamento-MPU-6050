#!/usr/bin/env python3

"""
TumbleGuard - Sistema Unificado
Inicia o servidor Flask e o detector de tombamento simultaneamente
"""

import multiprocessing
import time
import sys
import os

def run_server():
    """Executa o servidor Flask"""
    print("📡 Iniciando Servidor Flask...")
    from server import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_detector():
    """Executa o detector de tombamento"""
    # Aguarda 2 segundos para o servidor iniciar primeiro
    time.sleep(2)
    print("🔍 Iniciando Detector de Tombamento...")
    
    # Importa e executa a função main do detector
    from detector_tombamento import main
    main()

def iniciar():
    """Função principal que inicia ambos os processos"""
    print("=" * 60)
    print("🚗 TumbleGuard - Sistema de Detecção de Tombamento")
    print("=" * 60)
    print()
    
    # Descobre o IP
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "localhost"
    
    print(f"🌐 IP da Raspberry Pi: {ip}")
    print(f"📡 Servidor Flask: http://{ip}:5000")
    print(f"📝 Configuração: http://{ip}:5000/config")
    print()
    print("Pressione Ctrl+C para parar todos os serviços")
    print("=" * 60)
    print()
    
    # Cria processos separados
    server_process = multiprocessing.Process(target=run_server, name="FlaskServer")
    detector_process = multiprocessing.Process(target=run_detector, name="Detector")
    
    try:
        # Inicia ambos os processos
        server_process.start()
        detector_process.start()
        
        print(f"✅ Servidor Flask iniciado (PID: {server_process.pid})")
        print(f"✅ Detector iniciado (PID: {detector_process.pid})")
        print()
        
        # Aguarda os processos (roda indefinidamente)
        server_process.join()
        detector_process.join()
        
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print("🛑 Encerrando TumbleGuard...")
        print("=" * 60)
        
        # Para ambos os processos
        if server_process.is_alive():
            print("   Parando servidor Flask...")
            server_process.terminate()
            server_process.join(timeout=3)
        
        if detector_process.is_alive():
            print("   Parando detector...")
            detector_process.terminate()
            detector_process.join(timeout=3)
        
        print("✅ TumbleGuard encerrado com sucesso!")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        
        # Garante que os processos sejam encerrados
        if server_process.is_alive():
            server_process.terminate()
        if detector_process.is_alive():
            detector_process.terminate()
        
        sys.exit(1)

if __name__ == '__main__':
    # Necessário para multiprocessing no Python
    multiprocessing.set_start_method('spawn', force=True)
    iniciar()
