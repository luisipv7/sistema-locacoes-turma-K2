# template-INFO8B

Se o banco foi criado com uma versao antiga de `db01.sql`, execute no
PowerShell, na pasta do projeto:

```powershell
.\venv\Scripts\python.exe migrate_database.py
```

Depois reinicie a API. A migracao usa o `DATABASE_URL` do `.env`, adiciona
as colunas ausentes de `users` e recupera os separadores do hash inicial
caso ainda esteja no formato antigo. Pode ser executada novamente e preserva
os usuarios e suas senhas. Os usuarios antigos ficam sem `tenant_id` ate
serem vinculados a um tenant; as datas adicionadas recebem a data da migracao.

`SQLModel.metadata.create_all()` cria tabelas ausentes, mas nao atualiza
as colunas de tabelas existentes. O `db01.sql` atualizado serve para novas
instalacoes; bancos existentes precisam da migracao acima.
