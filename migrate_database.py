"""Atualiza a tabela users criada pela versao antiga de db01.sql."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def migrate_legacy_users(engine: Engine) -> list[str]:
    if engine.dialect.name != "mysql":
        raise RuntimeError("Esta migracao destina-se ao MySQL/MariaDB.")

    changes = []
    with engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("users"):
            raise RuntimeError("Tabela users ausente. Execute db01.sql primeiro.")
        columns = {column["name"] for column in inspector.get_columns("users")}
        # Os registros antigos recebem a data da migracao; a data original e desconhecida.
        additions = {
            "created_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "tenant_id": "INT NULL",
        }
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))
                changes.append(f"users.{name} adicionada")

        # Recupera somente os separadores do hash exato distribuido no SQL antigo.
        # O salt e o hash permanecem iguais, preservando a senha original.
        old_hash = (
            "pbkdf2_sha256$600000K5NUReY4sfCrQzbQLYx5jA=="
            "GpH9UhA9tooqUxeNU76S7BMUY9VzcXvIz/b1JiasbiM="
        )
        fixed_hash = (
            "pbkdf2_sha256$600000$K5NUReY4sfCrQzbQLYx5jA==$"
            "GpH9UhA9tooqUxeNU76S7BMUY9VzcXvIz/b1JiasbiM="
        )
        result = connection.execute(
            text("UPDATE users SET hashed_password = :fixed WHERE hashed_password = :old"),
            {"fixed": fixed_hash, "old": old_hash},
        )
        if result.rowcount:
            changes.append("Separadores do hash inicial recuperados")
    return changes


if __name__ == "__main__":
    from database import engine

    changes = migrate_legacy_users(engine)
    print("\n".join(changes) if changes else "Banco ja atualizado.")
