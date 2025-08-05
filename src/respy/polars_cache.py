import polars as pl
import urllib.parse
from pendulum import parse

from .interfaces import TableSettings, DataAddressString, META_TABLE, MetadataDictionary
from .utils import pop_data_at_address
import traceback


class PolarsCache:
    @staticmethod
    def convert_schema(schema: dict):
        return {
            k: v if not isinstance(v, str) else getattr(pl, v)
            for k, v in schema.items()
        }

    def __init__(
        self,
        table_settings: TableSettings,
        sub_tables_mapping: dict[DataAddressString, "PolarsCache"] = dict(),
        address_in_data: DataAddressString = None,
        inherited_key_column: list[str] = [],
    ):
        self._settings = table_settings

        # subtable addresses should be ignored
        self._settings["ignore_data_at_address"] += list(
            address
            for address in self._settings.get("sub_tables", {}).keys()
            if address not in self._settings
        )

        self.ignore_keys = self._settings["ignore_data_at_address"]

        self.key_column = TableSettings.COMPOSITE_JOIN.join(
            inherited_key_column + table_settings["composite_key"]
        )
        self.df_data: dict[str, list] = {
            k: list() for k in table_settings["polars_schema"].keys()
        }

        table_settings["polars_schema"].update({self.key_column: "String"})
        self.polars_schema = table_settings["polars_schema"]

        self.df_data.update({self.key_column: list()})

        self.meta = {k: list() for k in META_TABLE.schema.keys()}

        if len(sub_tables_mapping) == 0:
            self.sub_tables = dict()
            sub_tables_mapping = self.sub_tables
        else:
            sub_tables_mapping.update({address_in_data: self})
            self.sub_tables = sub_tables_mapping

        for sub_address, sub_settings in table_settings.get("sub_tables", {}).items():
            sub_settings["composite_key"] = (
                self._settings["composite_key"] + sub_settings["composite_key"]
            )
            PolarsCache(
                table_settings=sub_settings,
                sub_tables_mapping=sub_tables_mapping,
                address_in_data=sub_address,
            )

    def add_metadata(self, new_data: pl.DataFrame): ...

    def clear_cache(self):
        for k in self.df_data:
            self.df_data[k] = list()

    def execute_to_database(self, connection_str: str):
        print(f"executing {len(self.df_data)=} entries")
        pl.DataFrame(
            {k: v for k, v in self.df_data.items() if k != self.key_column},
            schema=PolarsCache.convert_schema(
                {
                    k: v
                    for k, v in self._settings["polars_schema"].items()
                    if k != self.key_column
                }
            ),
        ).write_database(
            table_name=self._settings["target_table"],
            connection=f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_str)}",
            if_table_exists="append",
        )
        self.clear_cache()
        for subtable in self.sub_tables.values():
            subtable.execute_to_database(connection_str=connection_str)

    def add_new_data(self, data: dict, parent_key_value=""):
        if self.key_column not in data:
            data[self.key_column] = TableSettings.COMPOSITE_JOIN.join(
                [parent_key_value]
                + [str(data[k]) for k in self._settings["composite_key"]]
            )

        key_value = data[self.key_column]

        for address in self._settings.get("sub_tables", {}).keys():
            popped_data = pop_data_at_address(data, address)
            self.sub_tables[address].add_data(popped_data, parent_key_value=key_value)

        for to_pop in self.ignore_keys:
            pop_data_at_address(data, to_pop)

        for k, v in data.items():
            self.df_data[k].append(v)
