## Run
Para rodar o backend voce deve executar todos os comandos dentro do ambiente virtual criado com as libs instaladas de acordo com o `requirements.txt` e todos os comandos devem estar dentro da pasta `backend/` caso contrario o banco e todas as outras coisas vão ser executadas no contexto errado então:
1. **Ative seu ambiente virtual de python**
2. **Rode para instalar dependencias:** `pip install -r requirements.txt`
3. **Rode:** `cd backend/` para entrar na pasta correta
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

estes podem ser copiados de `backend/.env.example`

A secret key pode ser gerada usando o seguinte comando no powershell do windows ou no terminal linux:
```bash
    openssl rand -base64 32
```

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
  ```json
  { "detail": "Já existe um usuário com este e-mail." }
  ```
- `422 Unprocessable Entity` — corpo inválido (por exemplo, e-mail inválido ou senha com menos de 8 caracteres).
  ```json
  {
    "detail": [
      { "msg": "...", "type": "..." }
    ]
  }
  ```

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
    "token_type": "bearer"
  }
  ```
- `401 Unauthorized` — e-mail ou senha inválidos.
  ```json
  { "detail": "E-mail ou senha inválidos." }
  ```
- `422 Unprocessable Entity` — corpo inválido (por exemplo, e-mail inválido ou campos ausentes).
  ```json
  {
    "detail": [
      { "msg": "...", "type": "..." }
    ]
  }
  ```
