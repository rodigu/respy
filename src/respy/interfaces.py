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


class SubTable(TypedDict):
    """assists in mapping data that should be directed to a different table.
    for instance, an API response that has a key in the return with list of objects value.
    the list of values may be directed to another table using the subtable settings.

    ## address in response data

    fed into `extract_endpoint_parameters_from_data`.
    see function documentation for implementation details.
    """

    address_in_response_data: DataAddressString
    table_settings: "TableSettings"


class TableSettings(TypedDict):
    """Settings for target tables in SQL database.

    ## schema

    polars [dataframe schema](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.schema.html)
    dictionary with column keys and polars type strings.

    ## target_table

    target table name string.

    ## sub tables

    dictionary of table name keys and subtable values.

    ## composite_key

    used to create a composite table key column.
    """

    schema: dict[str, str]
    target_table: SQLTableName
    sub_tables: Optional[dict[SQLTableName, SubTable]]
    composite_key: Optional[list[str]]


class APIEndpointConfiguration(TypedDict):
    """Configuration for an APIEndpoint."""

    api_endpoint: RawAPIEndpoint
    api_endpoint_parameters: Optional[dict]
    request_function_parameters: Optional[RequestFunctionParameters]
    dependent_requests: Optional[dict[RawAPIEndpoint, DataAddressString]]
    table_settings: TableSettings
    pagination_settings: Optional[PaginationSettings]


class RESTSQLConverterConfiguration(TypedDict):
    fetch_meta: APIEndpointConfiguration
    data: ResponseData
    table_settings: TableSettings


class EngineConfiguration(TypedDict):
    """endpoint configurations set at the engine level amy be overwritten by fetcher-level configuration."""

    domain: str
    endpoint_configuration_mapping: Optional[
        dict[RawAPIEndpoint, APIEndpointConfiguration]
    ]
    endpoints: list[APIEndpointConfiguration]


class EngineReturn(TypedDict):
    dependent_requests: Optional[list[APIEndpointConfiguration]]
