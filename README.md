# Detector de Tombamento com MPU-6050

> � Sistema de detecção de tombamento utilizando sensor MPU-6050 e Raspberry Pi com notificações via Telegram.

**Status:** 🚧 Em desenvolvimento (Projeto de TCC)

---

## 📋 Descrição

O **Detector de Tombamento com MPU-6050** é um sistema embarcado de segurança que monitora continuamente a inclinação de objetos, equipamentos ou estruturas através de um sensor acelerômetro/giroscópio MPU-6050. O sistema também conta com um módulo GPS GY-GPS6MV2 para rastreamento de localização. Quando um tombamento é detectado (inclinação superior a 45°), o sistema envia automaticamente um alerta de emergência via Telegram com a localização do dispositivo.

**Aplicações:**

- Veículos e máquinas pesadas
- Equipamentos industriais
- Containers e cargas
- Estruturas e mobiliário
- Qualquer objeto que necessite monitoramento de inclinação

---

## 🛠️ Tecnologias Utilizadas

- **Hardware:**
  - Raspberry Pi
  - Sensor MPU-6050 (Acelerômetro e Giroscópio)
  - Módulo GPS GY-GPS6MV2 (baseado no chip u-blox NEO-6M)

- **Software:**
  - Python 3
  - Comunicação I2C (SMBus)
  - API do Telegram (Bot)

---

## 📁 Estrutura do Projeto

```
Detector-de-tombamento-MPU-6050/
├── main.py                         # Ponto de entrada principal do sistema
├── detector_telegrambot/
│   └── detector_tombamento.py      # Módulo de detecção e alertas
├── config.json                     # Configurações do Telegram (token e chat_id)
└── README.md
```

---

## ⚙️ Funcionalidades

- ✅ Leitura contínua dos dados do acelerômetro (eixos X, Y, Z)
- ✅ Cálculo de inclinação em graus
- ✅ Detecção automática de tombamento (limite: 45°)
- ✅ Envio de alertas via Telegram Bot
- ✅ Cooldown de 60 segundos para evitar spam de notificações
- ✅ Exibição em tempo real do status no terminal

---

## 📦 Dependências

```bash
pip install requests smbus
```

---

## 🔌 Conexão do MPU-6050 com Raspberry Pi

| MPU-6050 | Raspberry Pi |
| -------- | ------------ |
| VCC      | 3.3V         |
| GND      | GND          |
| SDA      | GPIO 2 (SDA) |
| SCL      | GPIO 3 (SCL) |

---

## 🔌 Conexão do GPS GY-GPS6MV2 com Raspberry Pi

| GY-GPS6MV2 | Raspberry Pi  |
| ---------- | ------------- |
| VCC        | 3.3V ou 5V    |
| GND        | GND           |
| TX         | GPIO 15 (RXD) |
| RX         | GPIO 14 (TXD) |

---

## 🚀 Como Executar

1. **Habilite o I2C na Raspberry Pi:**

```bash
sudo raspi-config
# Interface Options > I2C > Enable
```

2. **Habilite a UART na Raspberry Pi (para o GPS):**

```bash
sudo raspi-config
# Interface Options > Serial Port
# "Would you like a login shell to be accessible over serial?" -> No
# "Would you like the serial port hardware to be enabled?" -> Yes
```

3. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/Detector-de-tombamento-MPU-6050.git
cd Detector-de-tombamento-MPU-6050
```

4. **Instale as dependências:**

```bash
pip install requests smbus
```

5. **Configure o Telegram:**

Crie um arquivo `config.json` na raiz do projeto:

```json
{
  "token": "SEU_TOKEN_DO_BOT",
  "chat_id": "SEU_CHAT_ID"
}
```

6. **Execute o sistema:**

```bash
python3 main.py
```

---

## 🤖 Configurando o Bot do Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Envie `/newbot` e siga as instruções para criar seu bot
3. Copie o **token** fornecido
4. Para obter seu **chat_id**, envie uma mensagem para o bot e acesse:
   ```
   https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
   ```

---

## Exemplo de Saída

```
============================================================
 Detector de Tombamento - Sistema de Monitoramento
============================================================

 IP da Raspberry Pi: 192.168.1.100
 Servidor Flask: http://192.168.1.100:5000

Pressione Ctrl+C para parar todos os serviços
============================================================

[0001] X=0.02 Y=-0.01 Z=1.00 | ✅ OK, 1.15°
[0002] X=0.03 Y=-0.02 Z=0.99 | ✅ OK, 2.06°
[0003] X=0.85 Y=0.45 Z=0.20 | ⚠️ TOMBADO, 78.32°
⚠️  🚨 TOMBAMENTO DETECTADO! Enviando alerta...
   ✅ Alerta enviado ao Telegram com sucesso!
```

---

## 📝 Parâmetros Configuráveis

| Parâmetro           | Valor Padrão | Descrição                                |
| ------------------- | ------------ | ---------------------------------------- |
| `MPU_ADDR`          | `0x68`       | Endereço I2C do sensor MPU-6050          |
| `LIMITE_TOMBAMENTO` | `45.0°`      | Ângulo limite para considerar tombamento |
| Cooldown de alerta  | `60s`        | Intervalo mínimo entre alertas           |

---

## 👨‍💻 Autor

Desenvolvido como Trabalho de Conclusão de Curso (TCC).

---

## 📄 Licença

Este projeto está em desenvolvimento para fins acadêmicos.
