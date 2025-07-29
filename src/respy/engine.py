from .utils import extract_endpoint_parameters_from_data, nested_merge_dictionary
from .interfaces import (
    APIEndpointConfiguration,
    EngineReturn,
    RawAPIEndpoint,
    ResponseData,
    EngineConfiguration,
    RESTSQLIntegratorConfiguration,
)
from .integrator import integrator
from .fetcher import fetch


def engine(configuration: EngineConfiguration) -> EngineReturn:
    dependent_requests: list[APIEndpointConfiguration] = list()

    fetched_data: dict[RawAPIEndpoint, ResponseData] = dict()

    for endpoint in configuration["endpoints"]:
        data = fetch(
            endpoint_configuration=endpoint,
            engine_configuration=configuration["engine"],
        )

        fetched_data.update({endpoint["api_endpoint"]: data})

        for dependent_endpoint, address_in_data in configuration["engine"][
            "endpoint_configuration_mapping"
        ][endpoint["api_endpoint"]]["dependent_requests"].items():
            endpoint_parameters = extract_endpoint_parameters_from_data(
                data=data, address_list=address_in_data.split(".")
            )
            for parameters in endpoint_parameters:
                dependent_requests.append(
                    {
                        "api_endpoint": dependent_endpoint,
                        "api_endpoint_parameters": parameters,
                    }
                )
    return {"dependent_requests": dependent_requests, "fetched_data": fetched_data}
