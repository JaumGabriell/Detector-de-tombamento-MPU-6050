# Guia de rotas

Exceto o cadastro público, as rotas abaixo exigem `Authorization: Bearer <access_token>`. As rotas marcadas como **admin** exigem administrador. `page` começa em 1; as listas têm 10 itens por página.

**Cadastro público — POST `/auth/`** — sem autenticação

Corpo: `{"name":"Maria","email":"maria@example.com","password":"senha123","admin":true}`. `admin` é opcional e usa `false` por padrão.

Resposta `201`: `{"id":1,"name":"Maria","email":"maria@example.com","admin":true}`

**Alterar administrador — PATCH `/admin/users/{user_id}/admin`** — admin

Corpo: `{"admin":true}` para conceder ou `{"admin":false}` para remover. A alteração deve ser em outra conta.

Resposta `200`: `{"id":2,"name":"Maria","email":"maria@example.com","admin":true}`

## Sensores

**Listar sensores — GET `/sensor/`** — usuário autenticado

Consulta opcional: `page`, `name`, `device_id` (UUID), `last_state` (`online`, `offline` ou `unknown`), `mqtt_enabled` (booleano).

```json
{"items":[{"id":1,"name":"Sensor 1","device_id":"550e8400-e29b-41d4-a716-446655440000","mqtt_username":"sensor-1","mqtt_enabled":true,"last_seen_at":null,"last_state":null,"telegram_accounts":[]}],"page":1,"total":1,"pages":1}
```

**Criar sensor — POST `/sensor/`** — admin

Corpo: `name`, `device_id` (UUID v4), `mqtt_username`, `mqtt_enabled` (opcional).

```json
{"name":"Sensor 1","device_id":"550e8400-e29b-41d4-a716-446655440000","mqtt_username":"sensor-1","mqtt_enabled":true}
```

Resposta `201`: `{"id":1,"name":"Sensor 1","device_id":"550e8400-e29b-41d4-a716-446655440000","mqtt_username":"sensor-1","mqtt_enabled":true,"last_seen_at":null,"last_state":null,"telegram_accounts":null}`

**Atualizar sensor — PUT `/sensor/{sensor_id}`** — admin

Corpo: os mesmos campos de criação. Resposta `200`: `{"id":1,"name":"Sensor 1","device_id":"550e8400-e29b-41d4-a716-446655440000","mqtt_username":"sensor-1","mqtt_enabled":true,"last_seen_at":null,"last_state":null,"telegram_accounts":[]}`

**Excluir sensor — DELETE `/sensor/{sensor_id}`** — admin

Resposta `200`: `{"message":"Sensor deletado com sucesso."}`

## Alertas e relatórios

**Listar alertas — GET `/admin/alerts`** — admin

Consulta opcional: `page`, `sensor_id`, `alert_type`, `start`, `end`. Datas ISO 8601 com fuso; limites inclusivos, aplicados a `occurred_at`. Exemplo: `start=2026-01-01T00:00:00Z`.

```json
{"items":[{"id":1,"event_id":"550e8400-e29b-41d4-a716-446655440000","sensor_id":1,"occurred_at":"2026-01-02T12:00:00","received_at":"2026-01-02T12:00:01","alert_type":"tilt","x":1.0,"y":2.0,"z":3.0,"inclination":45.0}],"page":1,"total":1,"pages":1}
```

**Excluir alerta — DELETE `/sensor/{sensor_id}/alert/{alert_id}`** — admin

Resposta `200`: `{"message":"Alerta deletado com sucesso."}`

**Exportar sensores — GET `/admin/reports/sensors`** — admin

Consulta opcional: `name`, `device_id`, `last_state`, `mqtt_enabled`, como na lista de sensores. Resposta `200`: arquivo CSV.

```csv
id,name,device_id,mqtt_username,mqtt_enabled,last_seen_at,last_state
1,Sensor 1,550e8400-e29b-41d4-a716-446655440000,sensor-1,True,,
```

**Exportar alertas — GET `/admin/reports/alerts`** — admin

Consulta opcional: `sensor_id`, `alert_type`, `start`, `end`, como na lista de alertas. Resposta `200`: arquivo CSV.

```csv
id,event_id,sensor_id,occurred_at,received_at,alert_type,x,y,z,inclination
1,550e8400-e29b-41d4-a716-446655440000,1,2026-01-02 12:00:00,2026-01-02 12:00:01,tilt,1.0,2.0,3.0,45.0
```

## Telegram

**Listar destinatários — GET `/admin/sensors/{sensor_id}/telegram-accounts`** — admin

Resposta `200`: `[{"id":1,"user_id":1,"username":null,"chat_id":123456}]`

**Vincular conta ao sensor — POST `/sensor/link/{sensor_id}/{telegram_account_id}`** — conta própria ou admin

Resposta `200`: `{"id":1,"name":"Sensor 1","device_id":"550e8400-e29b-41d4-a716-446655440000","mqtt_username":"sensor-1","mqtt_enabled":true,"last_seen_at":null,"last_state":null,"telegram_accounts":[{"id":1,"user_id":1,"username":null,"chat_id":123456}]}`

**Desvincular conta do sensor — DELETE `/sensor/link/{sensor_id}/{telegram_account_id}`** — conta própria ou admin

Resposta `200`: `{"message":"Conta do telegram desvinculada do sensor."}`

**Última telemetria — GET `/sensor/{sensor_id}/telemetry`** — usuário autenticado

Resposta `200`: `{"sensor_id":1,"connected":true,"data":{"x":1,"y":2,"z":3,"inclination":45,"latitude":null,"longitude":null,"occurred_at":"2026-01-01T00:00:00Z"}}`

`connected` indica que existe uma leitura armazenada; consulte `last_state` para o último estado MQTT conhecido.

## Sugestões para o frontend

| Sugestão | Rotas |
|---|---|
| F1 — Controlar acesso administrativo | `GET /auth/me` e respostas `403` das rotas administrativas |
| F2 — Painel de sensores | `GET /sensor/` |
| F3 — Central de alertas de todos os sensores | `GET /admin/alerts`, `GET /sensor/{sensor_id}/alert/{alert_id}` |
| F4 — Indicadores de monitoramento | `GET /sensor/`, `GET /admin/alerts`; agregação completa depende de implementação adicional |
| F5 — Exportar relatórios | `GET /admin/reports/sensors`, `GET /admin/reports/alerts` |
| F6 — Detalhar e editar sensores | `GET /sensor/{sensor_id}`, `POST /sensor/`, `PUT /sensor/{sensor_id}`, `DELETE /sensor/{sensor_id}`, `GET /admin/sensors/{sensor_id}/telegram-accounts`, rotas de vínculo acima |
| F7 — Monitorar sensor selecionado | `GET /sensor/`, `GET /sensor/{sensor_id}/telemetry` |
