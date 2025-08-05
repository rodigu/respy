import polars as pl
from .interfaces import RESTSQLIntegratorConfiguration, TableSettings


def integrator(configuration: RESTSQLIntegratorConfiguration) -> pl.DataFrame:
    df = pl.DataFrame(data=configuration["data"], schema=configuration["schema"])
