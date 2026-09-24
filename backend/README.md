## Run
Para rodar o backend voce deve executar todos os comandos dentro do ambiente virtual criado com as libs instaladas de acordo com o `requirements.txt` e todos os comandos devem estar dentro da pasta `backend/` caso contrario o banco e todas as outras coisas vão ser executadas no contexto errado então:
1. **Ative seu ambiente virtual de python**
2. **Rode:** `cd backend/` para entrar na pasta correta
3. **Rode para instalar dependencias:** `pip install -r requirements.txt`
4. **Configure o aruivo .env**
5. **Rode as migrations em:** [Migrations](#migrations)
6. **Rode para iniciar:** `python main.py`

## Migrations
**Comando para gerar arquivo de migração:** ``alembic revision --autogenerate -m "mensagem de migração"``
> [!WARNING]
> Usar somente quando modificar modelos do banco

**Comando para executar migrations:** ``alembic upgrade head``

> [!TIP]
> Usar sempre que deletar o banco de dados ou gerar nova migration

## ENV
O arquivo .env deve estar dentro de `backend/` e deve conter: 
* JWT_ACCESS_TOKEN_EXPIRE_MINUTES=tempo_em_minutos
* SECRET_KEY=
* HASH_ALGORITHM=algum_algoritmo_de_hashing
* TELEGRAM_BOT_TOKEN=
* TELEGRAM_BOT_USERNAME=MyTelegramBot
* TELEGRAM_WEBHOOK_SECRET=
* TELEGRAM_WEBHOOK_URL=https://seu.dominio.com/telegram/webhook

o algoritmo de hashing não é obrigatorio pois tem valor padrão dentro do codigo

estes podem ser copiados de `backend/.env.example`

A secret key e o telegram webhook secret podem ser gerados usando o seguinte comando no powershell do windows ou no terminal linux:
```bash
    openssl rand -base64 32
```
> [!warning]
> Porem o webhook secret que sera usado para grantir que as chamadas a este hook sejam legitimas do telegram não pode ter caracteres especiais, apenas aceitos caracteres de a-z, A-Z e numericos 0-9, portanto pode ser gerado usando o mesmo comando desde que removidos os outros caracteres

## Webhook
O **webhook** é usado para receber as mensagems enviadas ao bot no telegram, no momento a unica mensagem valida para o bot é `/start <validation_token>` para vincular uma conta de usuario da plataforma com um chat no telegram, essa vinculação serve para enviar alertas a usuarios especificos.
Porem como o telegram exige que o **webhook** seja `https` é preciso fornecer uma url com este protocolo, sendo necessario algum tipo de certificado valido, seja manualmente adquirido via `Lets Encrypt` e outras empresas ou qualquer outro metodo de deploy que forneça uma **URL** com `https` valido.
> [!TIP]
> Para facilitar na hora te testar pode ser util o uso do `Cloudflare Tunnel` ou `Ngrok` que fornecem tuneis criptografados com certificado valido.

## MQTT
Especificações nos arquivos `mqtt_sensor_state_spec.md`, `mqtt_sensor_alerts_spec.md`.

## Rotas

### Criar usuário

Método e rota: `POST /auth/`
Parâmetros de URL: nenhum.

Corpo da requisição:
```json
{
  "name": "Maria Silva",
  "email": "maria@email.com",
  "password": "senhaSegura123"
}
```

Respostas:

- `201 Created` — usuário criado.
  ```json
  {
    "id": 1,
    "name": "Maria Silva",
    "email": "maria@email.com",
    "admin": false
  }
  ```
- `409 Conflict` — já existe um usuário com o e-mail informado.
- `422 Unprocessable Entity` — corpo inválido.

### Login

Método e rota: `POST /auth/login`
Parâmetros de URL: nenhum.

Corpo da requisição:
```json
{
  "email": "maria@email.com",
  "password": "senhaSegura123"
}
```

Respostas:

- `200 OK` — credenciais válidas.
  ```json
  {
    "access_token": "<token JWT>",
    "refresh_token": "<token JWT>",
    "token_type": "Bearer"
  }
  ```
- `401 Unauthorized` — e-mail ou senha inválidos.
- `422 Unprocessable Entity` — corpo inválido.

### Login com formulário

Método e rota: `POST /auth/login-form`
Parâmetros de URL: nenhum.

Corpo da requisição: `username` e `password` em `application/x-www-form-urlencoded`.

Respostas:

- `200 OK` — credenciais válidas.
  ```json
  {
    "access_token": "<token JWT>",
    "refresh_token": "<token JWT>",
    "token_type": "Bearer"
  }
  ```
- `401 Unauthorized` — e-mail ou senha inválidos.

### Renovar token

Método e rota: `GET /auth/refresh`
Parâmetros de URL: nenhum.
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — tokens renovados.
  ```json
  {
    "access_token": "<token JWT>",
    "refresh_token": "<token JWT>",
    "token_type": "Bearer"
  }
  ```
- `401 Unauthorized` — token inválido ou usuário inexistente.

### Usuário autenticado

Método e rota: `GET /auth/me`
Parâmetros de URL: nenhum.
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — dados do usuário autenticado.
  ```json
  {
    "id": 1,
    "name": "Maria Silva",
    "email": "maria@email.com",
    "admin": false
  }
  ```
- `401 Unauthorized` — token inválido ou usuário inexistente.

### Criar sensor

Método e rota: `POST /sensor/`
Parâmetros de URL: nenhum.

Corpo da requisição:
```json
{
  "name": "Sensor 1",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "mqtt_username": "sensor-1",
  "mqtt_enabled": true
}
```

Respostas:

- `201 Created` — sensor criado.
  ```json
  {
    "id": 1,
    "name": "Sensor 1",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "mqtt_username": "sensor-1",
    "mqtt_enabled": true,
    "telegram_accounts": null
  }
  ```
- `409 Conflict` — username MQTT já associado a outro sensor.
- `422 Unprocessable Entity` — corpo inválido.

### Buscar sensor

Método e rota: `GET /sensor/{sensor_id}`
Parâmetros de URL: `sensor_id` (inteiro).

Respostas:

- `200 OK` — sensor encontrado.
  ```json
  {
    "id": 1,
    "name": "Sensor 1",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "mqtt_username": "sensor-1",
    "mqtt_enabled": true,
    "telegram_accounts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "maria_silva",
        "chat_id": 123456789
      }
    ]
  }
  ```
- `404 Not Found` — sensor não encontrado.

### Listar sensores

Método e rota: `GET /sensor/`
Parâmetros de URL: `page` (opcional, padrão `1`).

Respostas:

- `200 OK` — lista paginada de sensores.
  ```json
  {
    "items": [
      {
        "id": 1,
        "name": "Sensor 1",
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "mqtt_username": "sensor-1",
        "mqtt_enabled": true,
        "telegram_accounts": []
      },
      {
        "id": 2,
        "name": "Sensor 2",
        "device_id": "6ba7b810-9dad-41d1-80b4-00c04fd430c8",
        "mqtt_username": "sensor-2",
        "mqtt_enabled": true,
        "telegram_accounts": []
      }
    ],
    "page": 1,
    "total": 2,
    "pages": 1
  }
  ```

### Atualizar sensor

Método e rota: `PUT /sensor/{sensor_id}`
Parâmetros de URL: `sensor_id` (inteiro).

Corpo da requisição:
```json
{
  "name": "Sensor atualizado",
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "mqtt_username": "sensor-1",
  "mqtt_enabled": true
}
```

Respostas:

- `200 OK` — sensor atualizado.
  ```json
  {
    "id": 1,
    "name": "Sensor atualizado",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "mqtt_username": "sensor-1",
    "mqtt_enabled": true,
    "telegram_accounts": []
  }
  ```
- `404 Not Found` — sensor não encontrado.
- `422 Unprocessable Entity` — corpo inválido.
- `409 Conflict` — username MQTT já associado a outro sensor.

### Vincular sensor a conta do Telegram

Método e rota: `POST /sensor/link/{sensor_id}/{telegram_account_id}`
Parâmetros de URL: `sensor_id` e `telegram_account_id` (inteiros).

Respostas:

- `200 OK` — sensor vinculado à conta do Telegram.
  ```json
  {
    "id": 1,
    "name": "Sensor 1",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "telegram_accounts": [
      {
        "id": 1,
        "user_id": 1,
        "username": "maria_silva",
        "chat_id": 123456789
      }
    ]
  }
  ```
- `404 Not Found` — sensor ou conta do Telegram não encontrada.
- `409 Conflict` — conta do Telegram já associada ao sensor.

### Buscar alerta do sensor

Método e rota: `GET /sensor/{sensor_id}/alert/{alert_id}`
Parâmetros de URL: `sensor_id` e `alert_id` (inteiros).

Respostas:

- `200 OK` — alerta encontrado.
  ```json
  {
    "id": 1,
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "sensor_id": 1,
    "occurred_at": "2026-09-24T15:30:45Z",
    "received_at": "2026-09-24T15:30:46Z",
    "alert_type": "tilt",
    "x": 0.42,
    "y": -0.18,
    "z": 9.76,
    "inclination": 38.7
  }
  ```
- `404 Not Found` — sensor ou alerta não encontrado.

### Listar alertas do sensor

Método e rota: `GET /sensor/{sensor_id}/alert`
Parâmetros de URL: `sensor_id` (inteiro).
Parâmetros de consulta: `page` (opcional, padrão `1`).

Respostas:

- `200 OK` — lista paginada de alertas, do mais recente para o mais antigo.
  ```json
  {
    "items": [],
    "page": 1,
    "total": 0,
    "pages": 0
  }
  ```
- `404 Not Found` — sensor não encontrado.

### Excluir alerta do sensor

Método e rota: `DELETE /sensor/{sensor_id}/alert/{alert_id}`
Parâmetros de URL: `sensor_id` e `alert_id` (inteiros).

Respostas:

- `200 OK` — alerta deletado.
  ```json
  { "message": "Alerta deletado com sucesso." }
  ```
- `404 Not Found` — sensor ou alerta não encontrado.

### Excluir sensor

Método e rota: `DELETE /sensor/{sensor_id}`
Parâmetros de URL: `sensor_id` (inteiro).

Respostas:

- `200 OK` — sensor excluído.
  ```json
  { "message": "Sensor deletado com sucesso." }
  ```
- `404 Not Found` — sensor não encontrado.

### Receber webhook do Telegram

Método e rota: `POST /telegram/webhook`
Parâmetros de URL: nenhum.

Corpo da requisição: atualização JSON do Telegram.

Respostas:

- `200 OK` — webhook processado.
  ```json
  { "ok": true }
  ```

### Gerar vínculo com o Telegram

Método e rota: `POST /telegram/`
Parâmetros de URL: nenhum.
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — conta criada e link gerado.
  ```json
  { "connection_link": "<link de conexão>" }
  ```
- `401 Unauthorized` — token inválido.

### Listar contas do Telegram

Método e rota: `GET /telegram/`
Parâmetros de URL: nenhum.
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — lista paginada de contas do Telegram vinculadas.
  ```json
  {
    "id": 1,
    "user_id": 1,
    "username": "maria_silva",
    "chat_id": 123456789
  }
  ```
- `401 Unauthorized` — token inválido.
- `404 Not Found` — conta do Telegram não vinculada.

### Buscar conta específica do Telegram

Método e rota: `GET /telegram/{telegram_account_id}`
Parâmetros de URL: `telegram_account_id` (inteiro).
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — conta do Telegram encontrada.
  ```json
  {
    "id": 1,
    "user_id": 1,
    "username": "maria_silva",
    "chat_id": 123456789
  }
  ```
- `403 Forbidden` — a conta pertence a outro usuário.
- `404 Not Found` — conta do Telegram não encontrada.

### Desvincular conta do Telegram

Método e rota: `DELETE /telegram/`
Parâmetros de URL: nenhum.
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — conta desvinculada.
  ```json
  { "message": "Conta do telegram desvinculada com sucesso." }
  ```
- `401 Unauthorized` — token inválido.
- `404 Not Found` — conta do Telegram não vinculada.

### Atualizar chat do usuário

Método e rota: `PUT /chat/chat_id`
Cabeçalho: `Authorization: Bearer <token>`.

Corpo da requisição:
```json
{
  "chat_id": "123456789"
}
```

Respostas:

- `200 OK` — chat do usuário atualizado.
- `401 Unauthorized` — acesso inválido.
- `422 Unprocessable Entity` — corpo inválido.

### Buscar chat_ids

Método e rota: `GET /chat/chats_id`
Cabeçalho: `Authorization: Bearer <token>`.

Respostas:

- `200 OK` — lista de chat_ids disponíveis para o usuário.
  ```json
  [
    {
      "user_id": 1,
      "chat_id": 123456789
    }
  ]
  ```
- `401 Unauthorized` — acesso inválido.
