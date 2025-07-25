from typing import Optional
from interfaces import RequestParameters


def get_mapping_from(address_part: str) -> tuple[str, str]:
    split_address = address_part.split("}>{")
    return split_address[0][1:], split_address[1][:-1]


def extract_endpoint_parameters_from_data(
    data: dict | list,
    address_list: list[str],
    endpoint_parameters: Optional[RequestParameters] = None,
) -> list[RequestParameters]:
    """recursive function to extract parametrizable values from response data

    >>> data = [
    ... {"id": 1, "l": [{"id": "a"}, {"id": "b"}]},
    ... {"id": 2, "l": []},
    ... {"id": 3, "l": [{"id": "c"}, {"id": "d"}]},
    ... ]
    >>> address_list = '{id}>{customerID}.l.{id}>{itemID}'.split('.')
    >>> extract_endpoint_parameters_from_data(data=data,address_list=address_list)
    [{'customerID': 1, 'itemID': 'a'}, {'customerID': 1, 'itemID': 'b'}, {'customerID': 3, 'itemID': 'c'}, {'customerID': 3, 'itemID': 'd'}]
    >>> data = [{'id':1},{'id':2},{'id':3}]
    >>> address_list = ['{id}>{customerId}']
    >>> extract_endpoint_parameters_from_data(data=data,address_list=address_list)
    [{'customerId': 1}, {'customerId': 2}, {'customerId': 3}]

    :param dict | list data: data from response
    :param list[str] address_list: current chain of parameters being extracted from the data
    :param Optional[list[RequestParameters]] endpoint_parameters_list: address to parametrizable keys in data at list, defaults to None
    :param Optional[RequestParameters] endpoint_parameters: list of parameters, recursively generased, defaults to None
    :return list[RequestParameters]: list of request parameters extracted from the api response data
    """
    if len(address_list) == 0:
        return endpoint_parameters.copy()

    while isinstance(data, dict):
        address_part = address_list[0]
        data = data[address_part]
        address_list = address_list[1:]

    endpoint_parameters_list = list()

    for item in data:
        item_key, mapping = get_mapping_from(address_part=address_list[0])
        if endpoint_parameters is None:
            endpoint_parameters = dict()
        endpoint_parameters.update({mapping: item[item_key]})
        extraction = extract_endpoint_parameters_from_data(
            data=item,
            endpoint_parameters=endpoint_parameters,
            address_list=address_list[1:],
        )
        if isinstance(extraction, list):
            endpoint_parameters_list += extraction
        else:
            endpoint_parameters_list.append(extraction)

    return endpoint_parameters_list


def nested_merge_dictionary(d1: dict, d2: dict) -> dict:
    """creates a new dictionary that takes data from d1 and d2.
    keys with dictionary values are recursively created using values from d1 and d2.
    when keys that are not dictionary values exist in both d1 and d2, the value from d2 is used.
    """
    result = dict(d1)  # start with a shallow copy of d1
    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = nested_merge_dictionary(result[key], value)
        else:
            result[key] = value
    return result
