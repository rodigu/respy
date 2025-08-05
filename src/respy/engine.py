from .utils import extract_endpoint_parameters_from_data, nested_merge_dictionary
from .interfaces import (
    APIEndpointConfiguration,
    EngineReturn,
    RawAPIEndpoint,
    ResponseData,
    EngineConfiguration,
    RESTSQLIntegratorConfiguration,
    DataAddressString,
)
from .integrator import integrator
from .fetcher import fetch


def generate_dependent_configurations(
    data: dict, dependent_requests: dict[RawAPIEndpoint, DataAddressString]
):
    dependent_configurations: list[APIEndpointConfiguration] = list()

    for dependent_endpoint, address_in_data in dependent_requests.items():
        endpoint_parameters = extract_endpoint_parameters_from_data(
            data=data, address_list=address_in_data.split(".")
        )
        for parameters in endpoint_parameters:
            dependent_configurations.append(
                {
                    "api_endpoint": dependent_endpoint,
                    "api_endpoint_parameters": parameters,
                }
            )

    return dependent_configurations


def engine(configuration: EngineConfiguration) -> EngineReturn:
    dependent_requests: list[APIEndpointConfiguration] = list()

    fetched_data: dict[RawAPIEndpoint, ResponseData] = dict()

    for endpoint in configuration["endpoints"]:
        raw_api_endpoint = endpoint["api_endpoint"]

        endpoint_configuration: APIEndpointConfiguration = nested_merge_dictionary(
            configuration["endpoint_configuration_mapping"][raw_api_endpoint],
            endpoint,
        )
        data = fetch(
            domain=configuration["domain"], configuration=endpoint_configuration
        )

        integrator_configuration: RESTSQLIntegratorConfiguration = {
            "fetch_meta": endpoint_configuration,
            "data": data,
            "table_settings": endpoint_configuration["table_settings"],
        }

        integrator(configuration=integrator_configuration)

        fetched_data.update({endpoint["api_endpoint"]: data})

        dependent_requests += generate_dependent_configurations(
            data=data,
            dependent_requests=configuration["engine"][
                "endpoint_configuration_mapping"
            ][endpoint["api_endpoint"]]["dependent_requests"],
        )

    return {"dependent_requests": dependent_requests}
