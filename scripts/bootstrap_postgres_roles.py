"""One-time VNet-scoped bootstrap for least-privilege PostgreSQL Entra roles."""

import os
from contextlib import closing

import psycopg
from azure.identity import ManagedIdentityCredential
from psycopg import sql

from policy_rag.runtime import POSTGRES_TOKEN_SCOPE


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required")
    return value


def create_principal(cursor: psycopg.Cursor[object], name: str, object_id: str) -> None:
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (name,))
    if cursor.fetchone() is None:
        cursor.execute(
            "SELECT * FROM pg_catalog.pgaadauth_create_principal_with_oid(%s, %s, 'service', false, false)",
            (name, object_id),
        )


def main() -> None:
    admin_dsn = required("POSTGRES_ADMIN_DSN")
    application_dsn = required("POSTGRES_APPLICATION_DSN")
    application_name = required("APPLICATION_PRINCIPAL_NAME")
    application_object_id = required("APPLICATION_PRINCIPAL_OBJECT_ID")
    ingestion_name = required("INGESTION_PRINCIPAL_NAME")
    ingestion_object_id = required("INGESTION_PRINCIPAL_OBJECT_ID")
    credential = ManagedIdentityCredential(client_id=required("AZURE_CLIENT_ID"))
    try:
        token = credential.get_token(POSTGRES_TOKEN_SCOPE).token
        with closing(psycopg.connect(admin_dsn, password=token)) as connection:
            with connection.cursor() as cursor:
                create_principal(cursor, application_name, application_object_id)
                create_principal(cursor, ingestion_name, ingestion_object_id)
            connection.commit()

        with closing(psycopg.connect(application_dsn, password=token)) as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                for role_name in (application_name, ingestion_name):
                    cursor.execute(
                        sql.SQL("GRANT CONNECT ON DATABASE policy_rag TO {}").format(
                            sql.Identifier(role_name)
                        )
                    )
                    cursor.execute(
                        sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(
                            sql.Identifier(role_name)
                        )
                    )
                cursor.execute(
                    sql.SQL("GRANT CREATE ON SCHEMA public TO {}").format(
                        sql.Identifier(ingestion_name)
                    )
                )
                cursor.execute(
                    sql.SQL(
                        "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
                        "GRANT SELECT ON TABLES TO {}"
                    ).format(sql.Identifier(ingestion_name), sql.Identifier(application_name))
                )
                cursor.execute(
                    sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {}").format(
                        sql.Identifier(application_name)
                    )
                )
            connection.commit()
    finally:
        credential.close()
    print("PostgreSQL Entra application and ingestion roles are ready")


if __name__ == "__main__":
    main()
