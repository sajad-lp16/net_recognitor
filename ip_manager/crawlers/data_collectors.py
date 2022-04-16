import json
import ipaddress
from copy import deepcopy
from bs4 import BeautifulSoup

from ip_manager.utils.data_format import DATA_FORMAT, COUNTRY_CODE_MAPPER


def get_ip_range(network):
    if network is None:
        return None, None
    ip_range = tuple(ipaddress.ip_network(network).hosts())
    return str(int(ip_range[0])), str(int(ip_range[-1]))


def collect_ip_info(source):
    data_dict = json.loads(source)
    model_dict = deepcopy(DATA_FORMAT)
    try:
        model_dict["ip_network"] = data_dict.get("abuse").get("network")
        model_dict["ip_from"], model_dict["ip_to"] = get_ip_range(
            model_dict["ip_network"]
        )
    except AttributeError:
        pass
    try:
        model_dict["organization"] = data_dict.get("company").get("name")
    except AttributeError:
        pass
    try:
        model_dict["address"] = data_dict.get("abuse").get("address")
    except AttributeError:
        pass

    model_dict["city"] = data_dict.get("city")
    model_dict["region"] = data_dict.get("region")
    country_code = data_dict.get("country")
    if country_code is not None:
        model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
        model_dict["country"]["code"] = country_code
    else:
        model_dict["country"]["name"] = None
        model_dict["country"]["code"] = None
    location = data_dict.get("loc")
    if location is not None:
        model_dict["longitude"] = location.split(",")[0]
        model_dict["latitude"] = location.split(",")[1]
    try:
        model_dict["isp"]["name"] = data_dict.get("company").get("name")
    except AttributeError:
        try:
            model_dict["isp"]["name"] = data_dict.get("asn").get("name")
        except AttributeError:
            model_dict["isp"]["name"] = None
    return model_dict


def collect_ip_data_api(data):
    model_dict = deepcopy(DATA_FORMAT)
    try:
        model_dict["ip_network"] = data.get("asn").get("route")
        model_dict["ip_from"], model_dict["ip_to"] = get_ip_range(
            model_dict["ip_network"]
        )
    except AttributeError:
        pass

    try:
        model_dict["organization"] = data.get("asn").get("name")
    except AttributeError:
        pass
    model_dict["city"] = data.get("city")
    model_dict["region"] = data.get("region")
    country_code = data.get("country_code")
    if country_code is not None:
        model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
        model_dict["country"]["code"] = country_code
    else:
        model_dict["country"]["name"] = None
        model_dict["country"]["code"] = None
    model_dict["latitude"] = data.get("latitude")
    model_dict["longitude"] = data.get("longitude")
    try:
        model_dict["isp"]["name"] = data.get("asn").get("name")
    except AttributeError:
        pass
    return model_dict


def collect_ip_data(source):
    pass


def collect_my_ip_data(source):
    model_dict = deepcopy(DATA_FORMAT)

    def _get_dict_data(soup_obj):
        dict_data = {}
        elems = soup_obj.select("tr.odd") + soup_obj.select("tr.even")
        for elem in elems:
            try:
                keys = elem.select(".bold")
                if len(keys) >= 1:
                    try:
                        key, value, *_ = elem.text.split(": ")
                    except ValueError:
                        key, value, *_ = elem.text.split(":")
                    dict_data[key.strip()] = value.strip()
                if "country" in elem.text:
                    try:
                        _, country = elem.text.split(": ")
                    except ValueError:
                        _, country = elem.text.split(":")
                    dict_data["country_code"] = country.strip()
                elif "netname" in elem.text:
                    try:
                        _, isp = elem.text.split(": ")
                    except ValueError:
                        _, isp = elem.text.split(":")
                    dict_data["isp_name"] = isp.strip()
            except Exception as e:
                print(e)
                print(elem)
                break
        return dict_data

    soup = BeautifulSoup(source, "html.parser")
    data_dict = _get_dict_data(soup)

    data_mapping = {
        "address": "Owner Address",
        "organization": "IP Owner",
        "ip_network": "Owner CIDR",
    }
    model_dict["address"] = data_dict.get(data_mapping["address"])
    model_dict["organization"] = data_dict.get(data_mapping["organization"])
    model_dict["ip_network"] = data_dict.get(data_mapping["ip_network"])

    country_code = data_dict.get("country_code")
    if country_code is not None:
        model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
        model_dict["country"]["code"] = country_code

    isp_name = data_dict.get("isp_name")
    try:
        model_dict["isp"]["name"] = isp_name
    except AttributeError:
        pass

    model_dict["ip_from"], model_dict["ip_to"] = get_ip_range(model_dict["ip_network"])

    return model_dict
