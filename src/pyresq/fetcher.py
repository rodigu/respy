from requests import Response, get

from utils import nested_merge_dictionary
from interfaces import (
    APIEndpointConfiguration,
    EngineConfiguration,
    ResponseData,
)


def fetch(
    endpoint_configuration: APIEndpointConfiguration,
    engine_configuration: EngineConfiguration,
) -> ResponseData:
    raw_api_endpoint = endpoint_configuration["api_endpoint"]

    configuration = nested_merge_dictionary(
        engine_configuration["endpoint_configuration_mapping"][raw_api_endpoint],
        endpoint_configuration,
    )

    parametrized_api_endpoint = engine_configuration["domain"] + configuration[
        "api_endpoint"
    ].format(**configuration["api_endpoint_parameters"])

    response: Response = get(
        url=parametrized_api_endpoint, **configuration["request_function_parameters"]
    )

    if response.status_code != 200:
        raise BaseException(
            f"Details: [{response.status_code}: {response.reason}]\nFailed to call [{parametrized_api_endpoint}].\n[{configuration}]"
        )

    return response.json()
