from typing import Any

from clickhouse_sqlalchemy import (
    engines,
    get_declarative_base, 
    make_session, 
    types, 
    Table, 
)

from sqlalchemy import (
    create_engine,
    CursorResult,
    MetaData
)

from config.logging import Logger


class ClickhouseClient:
    def __init__(self, host: str, port: str, user: str, password: str, database: str, table: str) -> None:
        try:
            self.logger = Logger().setup_logger('rag-ch-client')
            self.dsn = f'clickhouse+{host}:{port}/{database}'
            self.engine = create_engine(self.dsn)
            self.session = make_session(self.engine)
            self.metadata = MetaData(bind=self.engine)
            self.Base = get_declarative_base(metadata=self.metadata)
            self.table = Table(table, self.metadata, autoload=True)
            self.logger.info(f" [*] Successfully connected to Clickhouse: {self.dsn}")
        except Exception as error:
            self.logger.error(f" [X] Error while connecting to Clickhouse: {error}")

    def execute_insert(self, values: dict[str]) -> CursorResult[Any]:
        """
        Executes INSERT query with given values in client to defined table.
        """
        query = self.table.insert()
        query.values(values)
        return self.session.execute(query)
    