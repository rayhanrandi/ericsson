from typing import Any, List

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
    def __init__(self, host: str, port: str, database: str, table: str, user: str = '', password: str = '') -> None:
        try:
            self.logger = Logger().setup_logger('consumer')
            self.dsn = f'clickhouse+http://{user}:{password}@{host}:{port}/{database}'
            self.engine = create_engine(url=self.dsn)
            self.session = make_session(self.engine)
            self.metadata = MetaData()
            self.table = table
            self.Base = get_declarative_base(metadata=self.metadata)
            self.logger.info(f" [*] Successfully connected to Clickhouse: {self.dsn}")
        except Exception as error:
            self.logger.error(f" [X] Error while connecting to Clickhouse: {error}")
    def execute_insert(self, values: dict[str]) -> CursorResult[Any]:
        """
        Executes INSERT query with given values in client to defined table.
        """
        return self.session.execute(Table(self.table, self.metadata, autoload_with=self.engine).insert().values(values))
    
    def execute_insert_batch(self, values_list: List[dict[str, Any]]) -> None:
        """
        Executes a batch INSERT query with a list of values into the defined table.
        """
        try:
            table_ref = Table(self.table, self.metadata, autoload_with=self.engine)

            # Prepare the insert query
            insert_query = table_ref.insert()
            self.logger.info(f"Inserting {values_list} rows into {self.table}.")

            # Execute batch insert
            self.session.execute(insert_query, values_list)
            self.session.commit()
            self.logger.info(f"Successfully inserted {len(values_list)} rows into {self.table}.")
        except Exception as e:
            self.logger.error(f"Error executing batch insert: {e}")
            self.session.rollback()
            raise
    