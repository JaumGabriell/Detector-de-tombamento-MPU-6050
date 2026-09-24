# Implementação do `state` MQTT no sensor físico
> [!WARNING]
> Arquivo gerado por IA com base nas especificações explicadas por mim ao modelo, este arquivo pode conter erros que eu não percebi, portanto use apenas como guia de configurações para a conexão mqtt com o backend. O arquivo foi revisado mas posso ter deixado alguma coisa passar. - Guilherme
## Objetivo deste documento

Este documento fornece contexto e requisitos para um agente de IA
implementar, no firmware do sensor físico, o mecanismo de **estado de
conectividade (`state`) via MQTT**.

O `state` existe para informar ao restante do sistema se o dispositivo
está atualmente conectado ao broker MQTT. Ele **não representa medições
do sensor e não representa eventos de tombamento**.

O agente deve tratar este documento como especificação funcional do
comportamento esperado no lado do dispositivo.

------------------------------------------------------------------------

## 1. Contexto da arquitetura

O sensor físico coleta dados e se comunica com um broker MQTT.

O backend é o responsável por consumir as mensagens MQTT, persistir
telemetria, processar alertas e disponibilizar informações ao frontend.

Existem três categorias principais de mensagens MQTT:

``` text
iot/v1/sensors/{sensor_id}/telemetry
iot/v1/sensors/{sensor_id}/alerts
iot/v1/sensors/{sensor_id}/state
```

Responsabilidades:

-   `telemetry`: envio da série histórica de medições.
-   `alerts`: envio de eventos importantes detectados pelo sensor.
-   `state`: indicação do estado atual de conectividade do dispositivo.

O agente responsável pelo firmware deve implementar apenas o
comportamento necessário para que o sensor publique corretamente seu
`state`.

------------------------------------------------------------------------

## 2. Significado do `state`

Inicialmente existem somente dois estados válidos:

``` text
online
offline
```

### `online`

Significa que o sensor:

-   possui conectividade suficiente para estabelecer uma sessão MQTT;
-   conseguiu se conectar e autenticar no broker;
-   está atualmente conectado ao broker.

### `offline`

Significa que a conexão MQTT do dispositivo foi perdida de forma
inesperada.

O sensor **não deve depender de conseguir publicar manualmente
`offline`** quando perde Wi-Fi, energia ou conectividade.

O estado `offline` deve ser publicado pelo próprio broker MQTT através
do mecanismo **Last Will and Testament (LWT)**.

------------------------------------------------------------------------

## 3. Tópico

Cada sensor possui seu próprio tópico de estado:

``` text
iot/v1/sensors/{sensor_id}/state
```

Exemplo para o sensor de ID `42`:

``` text
iot/v1/sensors/42/state
```

O `{sensor_id}` deve corresponder à identidade atribuída ao dispositivo.

Um sensor não deve publicar no tópico de outro sensor.

------------------------------------------------------------------------

## 4. Payload

O payload deve ser JSON.

### Estado online

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

### Estado offline

``` json
{
  "schema_version": 1,
  "state": "offline"
}
```

Não adicionar timestamps ao payload do LWT apenas para representar o
momento da desconexão.

O LWT é configurado no momento da conexão, mas pode ser publicado muito
tempo depois. Portanto, um timestamp criado quando o LWT é configurado
poderia representar incorretamente o momento em que o sensor ficou
offline.

O backend é responsável por registrar o momento em que recebe a mudança
de estado.

------------------------------------------------------------------------

## 5. QoS e Retain

Todas as publicações relacionadas ao `state` devem utilizar:

``` text
QoS = 1
Retain = true
```

### QoS 1

O QoS 1 fornece semântica de entrega "at least once".

Para o `state`, isso é adequado porque é mais importante que a mudança
de estado seja entregue do que evitar uma possível repetição da mesma
mensagem.

### Retain

`state` representa o **estado atual**, portanto deve ser uma retained
message.

Quando o broker recebe:

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

com `retain = true`, esse valor passa a ser o último estado conhecido
daquele sensor.

Um consumidor que assinar posteriormente o tópico poderá receber
imediatamente esse estado.

O mesmo vale para `offline`.

------------------------------------------------------------------------

## 6. Last Will and Testament (LWT)

O LWT é requisito obrigatório da implementação.

Antes de concluir a conexão MQTT, o cliente deve configurar uma Will
Message.

Para o sensor `42`:

### Will Topic

``` text
iot/v1/sensors/42/state
```

### Will Payload

``` json
{
  "schema_version": 1,
  "state": "offline"
}
```

### Will QoS

``` text
1
```

### Will Retain

``` text
true
```

A configuração da Will deve ocorrer **antes da conexão MQTT ser
estabelecida**.

Em pseudocódigo:

``` text
configurar cliente MQTT
configurar autenticação

configurar LWT:
    topic   = iot/v1/sensors/{sensor_id}/state
    payload = {"schema_version":1,"state":"offline"}
    qos     = 1
    retain  = true

conectar ao broker
```

------------------------------------------------------------------------

## 7. Publicação de `online`

Depois que a conexão MQTT for confirmada com sucesso, o sensor deve
publicar:

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

no tópico:

``` text
iot/v1/sensors/{sensor_id}/state
```

utilizando:

``` text
QoS = 1
Retain = true
```

A ordem deve ser:

``` text
configurar LWT
      ↓
conectar ao broker
      ↓
conexão MQTT confirmada
      ↓
publicar state=online
```

Não publicar `online` antes de a conexão MQTT estar efetivamente
estabelecida.

------------------------------------------------------------------------

## 8. Comportamento em uma falha inesperada

Considere:

``` text
Sensor
   │
   │ MQTT conectado
   ▼
Broker
```

Se ocorrer:

-   perda de energia;
-   perda abrupta de Wi-Fi;
-   perda de conectividade;
-   travamento/reboot inesperado;
-   interrupção da conexão TCP/WebSocket;
-   ausência prolongada detectada pelo mecanismo MQTT/keepalive;

o sensor pode não ter oportunidade de publicar nada.

Nesse caso, o broker deve detectar que a sessão foi perdida e publicar a
Will Message configurada anteriormente:

``` json
{
  "schema_version": 1,
  "state": "offline"
}
```

com `retain = true`.

Portanto:

``` text
Sensor perde conexão inesperadamente
              ↓
Broker detecta a perda
              ↓
Broker publica o LWT
              ↓
state = offline
              ↓
Backend recebe
```

Essa é a principal finalidade do LWT.

------------------------------------------------------------------------

## 9. Reconexão

O firmware deve implementar reconexão automática.

Quando a conexão for perdida, o sensor deve tentar restabelecer:

1.  conectividade de rede;
2.  conexão MQTT;
3.  autenticação MQTT.

Quando a conexão MQTT for novamente confirmada, o sensor deve publicar
novamente:

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

com:

``` text
QoS = 1
Retain = true
```

Fluxo esperado:

``` text
online
   ↓
perda de conexão
   ↓
broker publica LWT
   ↓
offline
   ↓
sensor tenta reconectar
   ↓
conexão restabelecida
   ↓
sensor publica online
   ↓
online
```

------------------------------------------------------------------------

## 10. O LWT deve ser configurado em cada nova conexão

O agente deve garantir que a configuração necessária do LWT seja
aplicada sempre que uma nova sessão/conexão MQTT exigir sua
configuração.

Não assumir que uma configuração realizada anteriormente continuará
válida depois que o cliente MQTT for destruído, recriado ou
reinicializado.

O código deve garantir a sequência:

``` text
criar/configurar cliente
        ↓
configurar LWT
        ↓
conectar
```

------------------------------------------------------------------------

## 11. Desconexão voluntária

Existe uma diferença entre:

``` text
falha inesperada
```

e:

``` text
desconexão intencional
```

Em uma desconexão MQTT normal/graciosa, o broker normalmente não deve
publicar o LWT como se tivesse ocorrido uma falha inesperada.

Se o firmware possuir um fluxo explícito de desligamento controlado e
for requisito informar `offline` nesse cenário, ele pode publicar
explicitamente:

``` json
{
  "schema_version": 1,
  "state": "offline"
}
```

com:

``` text
QoS = 1
Retain = true
```

antes da desconexão graciosa.

Esse comportamento é opcional para o protótipo.

A prioridade é garantir o funcionamento correto do LWT para falhas
inesperadas.

------------------------------------------------------------------------

## 12. Keep Alive

O cliente MQTT deve possuir um `keep alive` razoável.

Valor inicial recomendado para o projeto:

``` text
60 segundos
```

O keepalive ajuda o broker a perceber conexões que deixaram de funcionar
mesmo quando não houve fechamento TCP limpo.

Não implementar um mecanismo próprio de publicação contínua de
`state=online` apenas para funcionar como heartbeat, a menos que exista
posteriormente um requisito específico para isso.

O protocolo MQTT já possui mecanismos de manutenção/detecção da conexão.

------------------------------------------------------------------------

## 13. Não publicar `online` periodicamente

O sensor não precisa fazer:

``` text
online
online
online
online
online
```

a cada poucos segundos.

O estado é retained.

O comportamento normal deve ser:

``` text
conectou
   ↓
publica online uma vez
   ↓
permanece conectado
```

Quando desconectar inesperadamente:

``` text
broker publica offline
```

Quando reconectar:

``` text
sensor publica online novamente
```

Isso é suficiente para o modelo atual.

------------------------------------------------------------------------

## 14. `state` não é telemetria

Não colocar dados de sensores dentro do tópico `state`.

Exemplo incorreto:

``` json
{
  "state": "online",
  "angle": 32.5,
  "acceleration": 1.2
}
```

Esses valores pertencem a:

``` text
iot/v1/sensors/{sensor_id}/telemetry
```

O `state` deve permanecer pequeno e específico.

------------------------------------------------------------------------

## 15. `state` não representa alertas

Não utilizar valores como:

``` text
tilted
fallen
danger
alert
normal
```

como substitutos de `online/offline`.

Um tombamento é um evento de domínio e deve ser enviado através de:

``` text
iot/v1/sensors/{sensor_id}/alerts
```

Por exemplo:

``` json
{
  "schema_version": 1,
  "event_id": "...",
  "type": "EXCESSIVE_TILT",
  "value": 52.7,
  "threshold": 45.0
}
```

Portanto:

``` text
state     = conectividade/estado operacional
alerts    = eventos importantes
telemetry = medições
```

------------------------------------------------------------------------

## 16. Autenticação e autorização

O sensor deve utilizar sua própria credencial MQTT.

Exemplo conceitual:

``` text
client_id = sensor-42
username  = sensor-42
password  = segredo individual
```

A ACL do broker deve permitir que essa identidade publique somente nos
tópicos correspondentes ao próprio sensor.

Para `sensor-42`, por exemplo:

``` text
iot/v1/sensors/42/state
iot/v1/sensors/42/telemetry
iot/v1/sensors/42/alerts
```

O firmware não deve depender de conseguir publicar em tópicos de outros
sensores.

------------------------------------------------------------------------

## 17. Requisitos obrigatórios para a implementação

O agente deve garantir todos os seguintes requisitos:

1.  Construir o tópico de estado usando o ID real do sensor.
2.  Configurar LWT antes da conexão MQTT.
3.  LWT deve publicar `state=offline`.
4.  LWT deve utilizar QoS 1.
5.  LWT deve utilizar `retain=true`.
6.  Depois da conexão MQTT ser confirmada, publicar `state=online`.
7.  A publicação de `online` deve utilizar QoS 1.
8.  A publicação de `online` deve utilizar `retain=true`.
9.  Implementar reconexão automática.
10. Depois de cada reconexão bem-sucedida, publicar `online` novamente.
11. Não usar `state` para telemetria.
12. Não usar `state` para eventos de tombamento.
13. Não publicar `online` continuamente como heartbeat sem necessidade.
14. Não colocar no LWT um timestamp criado no momento da conexão como se
    fosse o horário futuro da desconexão.
15. Utilizar autenticação MQTT do próprio dispositivo.
16. Não desabilitar validações de segurança/TLS apenas para fazer a
    conexão funcionar.

------------------------------------------------------------------------

## 18. Comportamento esperado completo

O agente deve implementar comportamento equivalente ao seguinte
pseudocódigo:

``` text
inicializar dispositivo

conectar à rede

criar/configurar cliente MQTT

configurar credenciais MQTT

configurar:
    keep_alive = 60

configurar LWT:
    topic   = "iot/v1/sensors/{sensor_id}/state"
    payload = {
        "schema_version": 1,
        "state": "offline"
    }
    qos     = 1
    retain  = true

tentar conexão MQTT

quando MQTT conectar com sucesso:
    publicar:
        topic = "iot/v1/sensors/{sensor_id}/state"
        payload = {
            "schema_version": 1,
            "state": "online"
        }
        qos = 1
        retain = true

durante operação:
    manter processamento MQTT normalmente

se conexão for perdida:
    broker será responsável por publicar o LWT
    firmware inicia processo de reconexão

quando reconectar:
    publicar state=online novamente
```

------------------------------------------------------------------------

## 19. Critérios de teste

A implementação somente deve ser considerada correta depois dos
seguintes testes.

### Teste 1 --- conexão normal

1.  Iniciar sensor.
2.  Sensor conecta ao broker.
3.  Verificar tópico `state`.

Resultado esperado:

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

A mensagem deve estar retained.

### Teste 2 --- perda abrupta de energia

1.  Sensor está conectado e `online`.
2.  Remover energia sem executar desconexão MQTT.
3.  Aguardar o broker detectar a perda.

Resultado esperado:

``` json
{
  "schema_version": 1,
  "state": "offline"
}
```

Essa mensagem deve ter sido publicada pelo broker através do LWT e deve
ficar retained.

### Teste 3 --- reconexão

1.  Sensor encontra-se `offline`.
2.  Restaurar energia/conectividade.
3.  Sensor reconecta ao MQTT.

Resultado esperado:

``` json
{
  "schema_version": 1,
  "state": "online"
}
```

O retained anterior `offline` deve ser substituído pelo novo `online`.

### Teste 4 --- perda de Wi-Fi

1.  Manter sensor energizado.
2.  Derrubar sua conexão de rede.
3.  Aguardar detecção pelo broker.

Resultado esperado:

``` text
state → offline
```

4.  Restaurar Wi-Fi.

Resultado esperado:

``` text
sensor reconecta
state → online
```

### Teste 5 --- retained state

1.  Sensor está conectado e `online`.
2.  Iniciar um novo cliente MQTT.
3.  Assinar:

``` text
iot/v1/sensors/{sensor_id}/state
```

Resultado esperado:

O novo subscriber deve receber imediatamente o último `state` retained
sem precisar esperar uma nova publicação do sensor.

------------------------------------------------------------------------

## 20. Resultado final esperado

O comportamento observado pelo sistema deve ser:

``` text
                 SENSOR LIGA
                      │
                      ▼
                conecta MQTT
                      │
                      ▼
              publica ONLINE
                QoS 1 / retain
                      │
                      ▼
               ┌─────────────┐
               │   ONLINE    │
               └──────┬──────┘
                      │
              perda inesperada
                      │
                      ▼
              broker detecta
                      │
                      ▼
                publica LWT
                      │
                      ▼
              publica OFFLINE
                QoS 1 / retain
                      │
                      ▼
               ┌─────────────┐
               │   OFFLINE   │
               └──────┬──────┘
                      │
                sensor reconecta
                      │
                      ▼
              publica ONLINE
                      │
                      ▼
               ┌─────────────┐
               │   ONLINE    │
               └─────────────┘
```

O princípio central da implementação é:

> O sensor declara que está `online` quando consegue estabelecer sua
> conexão MQTT; o broker declara que ele está `offline` quando uma
> conexão previamente estabelecida é perdida inesperadamente.

Essa lógica permite que backend e frontend acompanhem a disponibilidade
dos dispositivos sem depender de uma mensagem de desligamento que o
sensor pode não conseguir enviar.
