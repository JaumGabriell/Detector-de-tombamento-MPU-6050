# Especificação MQTT — Alertas do sensor
> [!WARNING]
> Arquivo gerado por IA com base nas especificações explicadas por mim ao modelo, este arquivo pode conter erros que eu não percebi, portanto use apenas como guia de configurações para a conexão mqtt com o backend. O arquivo foi revisado mas posso ter deixado alguma coisa passar. - Guilherme
## Cadastro do sensor

O cadastro automático do sensor físico ainda não está definido.

Por enquanto:

1. Cadastre um novo sensor pela plataforma.
2. Consulte o `id` gerado para esse sensor no banco de dados.
3. Configure esse ID no sensor físico.
4. Use o ID no tópico MQTT para que o alerta seja associado ao sensor correto.

O ID usado no tópico é o ID inteiro do banco, não o `device_id` UUID.

## Conexão MQTT

O backend utiliza MQTT v5 sobre WebSockets.

Os dados de conexão são definidos no ambiente do backend:

```text
MQTT_HOST
MQTT_PORT       padrão: 443
MQTT_USERNAME
MQTT_PASSWORD
```

O cliente deve utilizar as credenciais aceitas pelo broker para publicação.

## Tópico de alerta

O sensor deve publicar neste formato:

```text
iot/v1/sensors/{sensor_id}/alerts
```

Exemplo para o sensor de ID `1`:

```text
iot/v1/sensors/1/alerts
```

O backend assina esse tópico com QoS `1`.

## QoS e confirmação de entrega

O fluxo deve utilizar QoS `1` na publicação dos alertas. Esse nível garante entrega "pelo menos uma vez": o broker pode entregar a mesma mensagem novamente, principalmente depois de uma queda de conexão.

O sensor não deve considerar o alerta confirmado apenas porque a publicação foi iniciada. O alerta deve permanecer pendente até o cliente MQTT confirmar que a mensagem foi aceita pelo broker, por exemplo através do callback de publicação ou do `PUBACK` da biblioteca utilizada.

Recomendações para o sensor:

- Publique os alertas com QoS `1`.
- Mantenha um buffer local para mensagens publicadas, mas ainda não confirmadas.
- Remova uma mensagem do buffer somente depois da confirmação do broker.
- Se a conexão cair, mantenha as mensagens pendentes e tente publicá-las novamente após a reconexão.
- Use armazenamento persistente para o buffer se o sensor puder reiniciar ou perder energia.
- Ao reenviar um alerta, mantenha exatamente o mesmo `event_id` e o mesmo conteúdo original.
- Não gere um novo `event_id` para cada tentativa de reenvio; isso faria o backend registrar duplicidades.
- Controle o tamanho do buffer e defina uma política para mensagens muito antigas, cheia ou sem espaço disponível.

O backend também pode receber uma mensagem mais de uma vez. Ele usa `event_id` como identificador único e ignora uma nova gravação quando esse ID já foi registrado.

O consumer do backend utiliza confirmação manual. Depois de processar a mensagem, ele envia o ACK para mensagens QoS `1`. Em caso de erro inesperado durante o processamento, a mensagem não é confirmada, permitindo que ela seja reenviada após a reconexão.

O sensor deve evitar QoS `0` para alertas de tombamento, pois nesse nível uma mensagem pode ser perdida durante uma queda de conexão. QoS `2` não é necessário para o fluxo atual.

### Retenção e sessão

Alertas não devem ser publicados como mensagens retidas (`retain = false`). Um alerta antigo não deve ser entregue como se fosse um evento novo quando o backend se conectar posteriormente.

O cliente MQTT do sensor deve usar um `client_id` estável e exclusivo. Não reutilize o mesmo `client_id` em dois sensores físicos ao mesmo tempo, pois o broker pode desconectar uma das sessões.

Se a biblioteca MQTT oferecer sessão persistente, ela pode ser utilizada para preservar mensagens pendentes no broker. Ainda assim, mantenha um buffer local para evitar perda de dados quando o sensor ficar sem acesso ao broker antes da publicação.

## Payload

O payload deve ser enviado como JSON UTF-8:

```json
{
  "schema_version": 1,
  "event_id": "8f14e45f-ea1a-4d3a-9f27-2c6b8a7d9012",
  "occurred_at": "2026-09-24T18:42:17Z",
  "type": "fall_detected",
  "x": 0.42,
  "y": -0.18,
  "z": 9.76,
  "inclination": 38.7
}
```

## Campos obrigatórios

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `schema_version` | `int` | Versão do formato do payload. |
| `event_id` | `UUID` | Identificador único do evento. |
| `occurred_at` | `datetime` | Data e hora do evento, preferencialmente em ISO 8601 UTC. |
| `type` | `string` | Tipo do alerta. |
| `x` | `float` | Medição do eixo X. |
| `y` | `float` | Medição do eixo Y. |
| `z` | `float` | Medição do eixo Z. |
| `inclination` | `float` | Inclinação calculada pelo sensor. |

Não enviar os campos `sequence`, `value` ou `threshold`.

## Processamento no backend

Ao receber um alerta, o backend:

1. Extrai o `sensor_id` do tópico.
2. Valida o JSON recebido.
3. Confirma que o sensor existe no banco.
4. Registra o alerta na tabela `sensor_alerts`.
5. Atualiza `last_seen_at` e `last_state` do sensor.
6. Envia o alerta para as contas Telegram vinculadas ao sensor.

O `event_id` deve ser único. Se o mesmo evento for publicado novamente, ele não será registrado duas vezes.

## Regras importantes

- O tópico deve usar `alerts` no plural.
- O `sensor_id` deve ser numérico.
- O JSON deve conter todos os campos obrigatórios.
- `event_id` deve ser um UUID válido.
- Os campos `x`, `y`, `z` e `inclination` devem ser números reais.
- `occurred_at` deve estar em formato de data e hora válido.
