from typing import Optional, TypedDict, Literal
from requests import Response, get

type RawAPIEndpoint = str
type ResponseData = dict | list


class RequestJSON(TypedDict):
    """Request JSON payload."""


class RequestParameters(TypedDict):
    """Request parameters."""


class RequestFunctionParameters(TypedDict):
    """Parameters for one of Python's `request` functions (GET, PUT, etc) parameters."""

    headers: dict
    params: Optional[RequestParameters]
    json: Optional[RequestJSON]


type DataAddressString = str
type SQLTableName = str
type ResponseDataKey = str


class PAGINATION_TYPES:
    FixedPaginationParameter = "FixedPaginationParameter"
    VariablePaginationParameter = "VariablePaginationParameter"
    OffsetPagination = "OffsetPagination"
    AddressedPagination = "AddressedPagination"
    CursorPagination = "CursorPagination"


class PaginationSettings(TypedDict):
    pagination_type: str


class FixedPaginationParameter(PaginationSettings):
    """Pagination parameter set at configuration."""

    parameter_name: str
    value: int | str


class VariablePaginationParameter(PaginationSettings):
    """Pagination parameter set by response data.

    `parameter_name` refers to a parameter name for a `requests` function `params`
    `value_address_in_data_response` contains the address for the parameter value in the response data.
    """

    parameter_name: str
    value_address_in_data_response: DataAddressString


class OffsetPagination(PaginationSettings):
    """Same as page-based pagination (page size and page number)."""

    limit: FixedPaginationParameter
    offset: FixedPaginationParameter


class AddressedPagination(PaginationSettings):
    """Address in the response data for the next page."""

    next_endpoint_address: Optional[DataAddressString]


class CursorPagination(PaginationSettings):
    """Pagination based on cursors -- bookmarks that stand for a point of reference in the paged request data."""

    cursor: VariablePaginationParameter
    limit: FixedPaginationParameter


# mapping from column names into SQL types
type SQLColumnTypeMapping = dict[str, str]
# dictionary given to `polars.DataFrame` `schema` kwarg
type PolarsSchema = dict[str, any]
# mapping from column names (final, after normalization) to their date conversion strings (used in `strptime`)
type DateColumnParseMapping = dict[str, str]


class TableSettings(TypedDict):
    """Settings for target tables in SQL database.

    used by the integrator.

    ## polars_schema

    polars [dataframe polars_schema](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.polars_schema.html)
    dictionary with column keys and polars type strings.

    ## target_table

    target table name string.

    ## sub tables

    dictionary of address in data keys and subtable values.
    address fed into `extract_endpoint_parameters_from_data`.
    see function documentation for implementation details.

    all addresses in the subtable keys get popped fro mthe data dictionary before integration.

    ## composite_key

    parent composite keys are concatenated and appended as a prefix
    into the composite key of the child entry.

    used to create a composite key column at the target table.
    if the composite key list is ['id','content.category'], it is joined using `:`,
    a column 'id:content.category' will be created and used of updating, insertion, etc.

    the dot syntax signifies nested data ('content': {'category':...}).

    in the case of a simple (non-composite),
    a value for the property should still be specified.

    # meta_table

    meta_table name.
    if left undefined, the meta-table will be named using the convention
    of a `_META` prefix followed by the table name: `f_META_{target_table}`.
    """

    COMPOSITE_JOIN = ":"
    polars_schema: PolarsSchema
    date_columns_parsing_string: DateColumnParseMapping
    target_table: SQLTableName
    sub_tables: Optional[dict[DataAddressString, "TableSettings"]]
    composite_key: list[str]
    ignore_data_at_address: Optional[list[DataAddressString]]


class MetadataDictionary(TypedDict):
    _IS_DELETED: list
    _DT_DELETED: list
    _DT_LAST_UPDATED: list
    _DT_CREATED: list
    _KEY: list
    _SOURCE_TABLE_NAME: list


class META_TABLE:
    DELETED_FLAG = "_IS_DELETED"
    DT_DELETED = "_DT_DELETED"
    DT_LAST_UPDATED = "_DT_LAST_UPDATED"
    DT_CREATED = "_DT_CREATED"
    KEY_COLUMN = "_KEY"
    SOURCE_TABLE_NAME = "_SOURCE_TABLE_NAME"
    schema: PolarsSchema = {
        DELETED_FLAG: "Boolean",
        DT_DELETED: "Datetime",
        DT_LAST_UPDATED: "Datetime",
        DT_CREATED: "Datetime",
        SOURCE_TABLE_NAME: "String",
    }
    SQL_types: SQLColumnTypeMapping = {}


class APIEndpointConfiguration(TypedDict):
    """Configuration for an APIEndpoint."""

    api_endpoint: RawAPIEndpoint
    api_endpoint_parameters: Optional[dict]
    request_function_parameters: Optional[RequestFunctionParameters]
    dependent_requests: Optional[dict[RawAPIEndpoint, DataAddressString]]
    table_settings: Optional[TableSettings]
    pagination_settings: Optional[PaginationSettings]


class RESTSQLIntegratorConfiguration(TypedDict):
    fetch_meta: APIEndpointConfiguration
    data: ResponseData
    table_settings: TableSettings


class SQLTableCreatorConfiguration(TypedDict):
    table_name: SQLTableName
    table_column_mapping: SQLColumnTypeMapping


class EngineConfiguration(TypedDict):
    """endpoint configurations set at the engine level may be overwritten by fetcher-level configuration.

    tables dictionary with type mapping is used to create tables when they don't exist in the database.
    """

    domain: str
    endpoint_configuration_mapping: Optional[
        dict[RawAPIEndpoint, APIEndpointConfiguration]
    ]
    endpoints: list[APIEndpointConfiguration]
    tables_column_types: dict[SQLTableName, SQLColumnTypeMapping]
    meta_table_name: SQLTableName


class EngineReturn(TypedDict):
    dependent_requests: Optional[list[APIEndpointConfiguration]]
