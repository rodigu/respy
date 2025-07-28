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
    address_in_response_data: DataAddressString
    table_settings: "TableSettings"


class TableSettings(TypedDict):
    type_mapping: dict[str, str]
    target_table: SQLTableName
    sub_tables: Optional[dict[SQLTableName, SubTable]]


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
    type_mapping: dict[str, str]


class EngineConfiguration(TypedDict):
    """endpoint configurations set at the engine level amy be overwritten by fetcher-level configuration."""

    domain: str
    endpoint_configuration_mapping: Optional[
        dict[RawAPIEndpoint, APIEndpointConfiguration]
    ]
    endpoints: list[APIEndpointConfiguration]


class EngineReturn(TypedDict):
    dependent_requests: Optional[list[APIEndpointConfiguration]]
    fetched_data: ResponseData
