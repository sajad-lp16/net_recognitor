import json
import ipaddress
from copy import deepcopy

from ip_manager.utils.data_format import DATA_FORMAT, COUNTRY_CODE_MAPPER


def get_ip_range(network):
    ip_range = tuple(ipaddress.ip_network(network).hosts())
    return ip_range[0], ip_range[-1]


def collect_ip_info(source):

    data_dict = json.loads(source)
    model_dict = deepcopy(DATA_FORMAT)
    try:
        model_dict["ip_network"] = data_dict.get("abuse").get("network")
        model_dict["ip_from"], model_dict["ip_to"] = get_ip_range(
            model_dict["ip_network"]
        )
    except AttributeError:
        model_dict["ip_network"] = None
        model_dict["ip_from"] = None
        model_dict["ip_to"] = None
    try:
        model_dict["organization"] = data_dict.get("company").get("name")
    except AttributeError:
        model_dict["organization"] = None
    try:
        model_dict["address"] = data_dict.get("abuse").get("address")
    except AttributeError:
        model_dict["address"] = None

    model_dict["city"] = data_dict.get("city")
    model_dict["region"] = data_dict.get("region")
    try:
        country_code = data_dict.get("country")
        model_dict["country"]["name"] = COUNTRY_CODE_MAPPER[country_code]
        model_dict["country"]["code"] = country_code
    except AttributeError:
        model_dict["country"]["code"] = None
    location = data_dict.get("loc").split(",")
    if location is not None:
        model_dict["longitude"] = location[0]
        model_dict["latitude"] = location[1]
    try:
        model_dict["isp"]["name"] = data_dict.get("company").get("name")
    except AttributeError:
        try:
            model_dict["isp"]["name"] = data_dict.get("asn").get("name")
        except AttributeError:
            model_dict["isp"]["name"] = None
    return model_dict
