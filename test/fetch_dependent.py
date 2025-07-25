from json import load, dump
from requests import post
from typing import TypedDict

import pyresq.engine as engine
import pyresq.interfaces as interfaces

from config.l_sales import configuration as tst_config
# from config.jp_tst import configuration as tst_config

_other_headers_default = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
}


def get_token(
    base_url: str, user: str, password: str, other_headers=_other_headers_default
):
    return post(
        url=f"{base_url}/api/auth",
        json={"usuario": user, "senha": password},
        headers=other_headers,
    )


def load_conf() -> interfaces.EngineConfiguration:
    conf = tst_config

    with open("./test/config/l_auth.json") as f:
        l_auth = load(f)["prod"]

    token = get_token(base_url=l_auth["base_url"], **l_auth["auth"]).json()["token"]

    for endpoint in conf["engine"]["endpoint_configuration_mapping"].values():
        endpoint["request_function_parameters"]["headers"]["Authorization"] = (
            f"Bearer {token}"
        )

    return conf


if __name__ == "__main__":
    conf = load_conf()
    dependent = engine.engine(configuration=conf)

    dependent_data = []
    for endpoint_configuration in dependent["dependent_requests"][:3]:
        fd = engine.fetch(
            endpoint_configuration=endpoint_configuration,
            engine_configuration=conf["engine"],
        )
        dependent_data.append(fd)
    print(dependent_data)
