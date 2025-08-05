from requests import Response, get

from .utils import nested_merge_dictionary
from .interfaces import (
    APIEndpointConfiguration,
    EngineConfiguration,
    ResponseData,
)


def fetch(
    domain: str,
    configuration: APIEndpointConfiguration,
) -> ResponseData:
    parametrized_api_endpoint = domain + configuration["api_endpoint"].format(
        **configuration["api_endpoint_parameters"]
    )

    response: Response = get(
        url=parametrized_api_endpoint, **configuration["request_function_parameters"]
    )

    if response.status_code != 200:
        raise BaseException(
            f"Details: [{response.status_code}: {response.reason}]\nFailed to call [{parametrized_api_endpoint}].\n>Params[{configuration['request_function_parameters'].get('params', None)}]"
        )

    return response.json()
