import re
import json
import ipaddress
from copy import deepcopy
from bs4 import BeautifulSoup

from ip_manager.utils.data_format import DATA_FORMAT, COUNTRY_CODE_MAPPER


class BaseCollector:
    @staticmethod
    def _get_ip_range(network):
        if network is None:
            return None, None
        network_obj = ipaddress.ip_network(network)
        first = int(network_obj.network_address)
        last = int(network_obj.broadcast_address)
        return str(first), str(last)

    @staticmethod
    def _get_ip_version(network):
        if network is None:
            return
        network_obj = ipaddress.ip_network(network)
        if network_obj.__class__.__name__ == "IPv6Address":
            return 6
        return 4

    @staticmethod
    def set_city_country(model_dict, data):
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


class IPInfoCollector(BaseCollector):
    def login_collect(self, source):
        data_dict = json.loads(source)
        model_dict = deepcopy(DATA_FORMAT)
        self.set_city_country(model_dict, data_dict)
        try:
            network = data_dict.get("abuse").get("network")
            model_dict["ip_network"] = network
            model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
                model_dict["ip_network"]
            )
            model_dict["version"] = self._get_ip_version(network)
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

    def no_login_collector(self, source):
        def _extract_field(pat):
            try:
                return json.loads(re.findall(pat, source)[0])
            except IndexError:
                return

        model_dict = deepcopy(DATA_FORMAT)

        city_pattern = r"city: (.*)\n"
        region_pattern = r"region: (.*)\n"
        location_pattern = r"loc: (.*)\n"
        country_pattern = r"country: (.*)\n"
        org_pattern = r"org: (.*)\n"
        network_pattern = r"network: (.*)\n"
        address_pattern = r"address: (.*)\n"
        isp_name_pattern = r"\bname: (.*)\n"

        location_data = _extract_field(location_pattern)
        ip_network = _extract_field(network_pattern)
        country_code = _extract_field(country_pattern)
        country_name = COUNTRY_CODE_MAPPER.get(country_code)

        model_dict["isp"] = {"name": _extract_field(isp_name_pattern)}
        model_dict["city"] = _extract_field(city_pattern)
        model_dict["region"] = _extract_field(region_pattern)
        model_dict["ip_network"] = ip_network
        model_dict["version"] = self._get_ip_version(ip_network)
        model_dict["country"] = {
            "name": country_name,
            "code": country_code,
        }
        model_dict["organization"] = _extract_field(org_pattern)
        model_dict["address"] = _extract_field(address_pattern)
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(ip_network)
        if location_data is not None:
            model_dict["longitude"] = location_data.split(",")[0]
            model_dict["latitude"] = location_data.split(",")[1]

        return model_dict


class IPDataCollector(BaseCollector):
    def login_collect(self, data):
        model_dict = deepcopy(DATA_FORMAT)
        self.set_city_country(model_dict, data)
        try:
            model_dict["ip_network"] = data.get("asn").get("route")
            model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
                model_dict["ip_network"]
            )
            model_dict["version"] = self._get_ip_version(network)
        except AttributeError:
            pass
        try:
            model_dict["isp"]["name"] = data.get("asn").get("name")
        except AttributeError:
            pass
        try:
            model_dict["organization"] = data.get("asn").get("name")
        except AttributeError:
            pass
        return model_dict

    def collect(self, source):
        pass


class MyIPCollector(BaseCollector):
    def login_collect(self, source):
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
        network = data_dict.get(data_mapping["ip_network"])
        model_dict["address"] = data_dict.get(data_mapping["address"])
        model_dict["organization"] = data_dict.get(data_mapping["organization"])
        model_dict["ip_network"] = network
        model_dict["version"] = self._get_ip_version(network)

        country_code = data_dict.get("country_code")
        if country_code is not None:
            model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
            model_dict["country"]["code"] = country_code

        isp_name = data_dict.get("isp_name")
        try:
            model_dict["isp"]["name"] = isp_name
        except AttributeError:
            pass

        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
            model_dict["ip_network"]
        )

        return model_dict


class RipeCollector(BaseCollector):
    def login_collect(self, source):
        pass

    @staticmethod
    def no_login_collect(source):
        model_data = deepcopy(DATA_FORMAT)
        try:
            source = source["objects"]["object"]
        except KeyError:
            return model_data
        for data_fields in source:
            if data_fields.get("type") == "inetnum":
                try:
                    source = data_fields.get("attributes").get("attribute")
                except AttributeError:
                    return model_data
                for item in source:
                    if item.get("name") == "country":
                        model_data["country"]["code"] = item.get("value")
                    elif item.get("name") == "mnt-by":
                        model_data["isp"]["name"] = item.get("value")
                    elif item.get("name") == "geoloc":
                        location = item.get("value").split(" -")
                        model_data["longitude"] = location[0]
                        model_data["latitude"] = location[1]
                    elif item.get("name") == "netname":
                        model_data["organization"] = item.get("value")
                    elif item.get("name") == "inetnum":
                        ip_range = item.get("value").split(" - ")
                        model_data["ip_from"] = str(
                            int(ipaddress.ip_address(ip_range[0]))
                        )
                        model_data["ip_to"] = str(
                            int(ipaddress.ip_address(ip_range[1]))
                        )
        return model_data
