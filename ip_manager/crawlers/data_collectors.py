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
    def _get_version_network(network):
        if network is None:
            return
        network_obj = ipaddress.ip_network(network)
        if network_obj.__class__.__name__ == "IPv6Network":
            return 6
        return 4

    @staticmethod
    def _get_version_ip(ip):
        if ip is None:
            return
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.__class__.__name__ == "IPv6Address":
            return 6
        return 4

    @staticmethod
    def set_country(model_dict, data):
        country_code = data.get("country_code")
        if country_code is not None:
            model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
            model_dict["country"]["code"] = country_code
        else:
            model_dict["country"]["name"] = None
            model_dict["country"]["code"] = None

    def version_setter(self, model_dict):
        if model_dict["ip_network"] is None:
            model_dict["version"] = self._get_version_ip(model_dict["ip_from"])
        else:
            model_dict["version"] = self._get_version_network(model_dict["ip_network"])
        return model_dict

    @staticmethod
    def get_field(pat, target):
        if target is None:
            return
        data = re.findall(pat, target)
        if data:
            return data[0]


class IPInfoCollector(BaseCollector):
    def __init__(self):
        self.city_pattern = r"city: (.*)\n"
        self.region_pattern = r"region: (.*)\n"
        self.location_pattern = r"loc: (.*)\n"
        self.country_pattern = r"country: (.*)\n"
        self.org_pattern = r"org: (.*)\n"
        self.network_pattern = r"network: (.*)\n"
        self.address_pattern = r"address: (.*)\n"
        self.isp_name_pattern = r"\bname: (.*)\n"

    def login_collect(self, source):
        data_dict = json.loads(source)
        model_dict = deepcopy(DATA_FORMAT)
        self.set_country(model_dict, data_dict)
        model_dict["city"] = data_dict.get("city")
        model_dict["region"] = data_dict.get("region")
        model_dict["latitude"] = data_dict.get("latitude")
        model_dict["longitude"] = data_dict.get("longitude")
        try:
            network = data_dict.get("abuse").get("network")
            model_dict["ip_network"] = network
            model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
                model_dict["ip_network"]
            )
            model_dict["version"] = self._get_version_network(network)
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
        return self.version_setter(model_dict)

    def no_login_collector(self, source):
        def _extract_field(pat):
            try:
                return json.loads(re.findall(pat, source)[0])
            except IndexError:
                return

        model_dict = deepcopy(DATA_FORMAT)
        location_data = _extract_field(self.location_pattern)
        ip_network = _extract_field(self.network_pattern)
        country_code = _extract_field(self.country_pattern)
        country_name = COUNTRY_CODE_MAPPER.get(country_code)

        model_dict["isp"] = {"name": _extract_field(self.isp_name_pattern)}
        model_dict["city"] = _extract_field(self.city_pattern)
        model_dict["region"] = _extract_field(self.region_pattern)
        model_dict["ip_network"] = ip_network
        model_dict["version"] = self._get_version_network(ip_network)
        model_dict["country"] = {
            "name": country_name,
            "code": country_code,
        }
        model_dict["organization"] = _extract_field(self.org_pattern)
        model_dict["address"] = _extract_field(self.address_pattern)
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(ip_network)
        if location_data is not None:
            model_dict["longitude"] = location_data.split(",")[0]
            model_dict["latitude"] = location_data.split(",")[1]

        return self.version_setter(model_dict)


class IPDataCollector(BaseCollector):
    def __init__(self):

        self.city_pattern = r'\n*CITY\n([^\n]+)\n'
        self.region_pattern = r'\n*REGION NAME\n([^\n]+)\n'
        self.country_code_pattern = r'\n*COUNTRY CODE\n([^\n]+)\n'
        self.latitude_pattern = r'\n*LATITUDE\n([^\n]+)\n'
        self.longitude_pattern = r'\n*LONGITUDE\n([^\n]+)\n'
        self.organization_pattern = r'\n*ORGANIZATION\n([^\n]+)\n'
        self.ip_network_pattern = r'\n*ROUTE\n([^\n]+)\n'

        self.asn_pattern_n = r"asn: {[^}]+}"
        self.company_pattern_n = r"company: {[^}]+}"
        self.name_pattern_n = r'name: "([^"]+)"'
        self.region_pattern_n = r'region: "([^"]+)"'
        self.country_code_pattern_n = r'country_code: "([^"]+)"'
        self.latitude_pattern_n = r"latitude: ([^\n,]+)"
        self.longitude_pattern_n = r"longitude: ([^\n,]+)"
        self.ip_network_pattern_n = r'route: "([^\n,]+)"'

    def login_api_collect(self, data):
        model_dict = deepcopy(DATA_FORMAT)
        self.set_country(model_dict, data)
        model_dict["city"] = data.get("city")
        model_dict["region"] = data.get("region")
        model_dict["latitude"] = data.get("latitude")
        model_dict["longitude"] = data.get("longitude")
        try:
            network = data.get("asn").get("route")
            model_dict["ip_network"] = network
            model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(network)
            model_dict["version"] = self._get_version_network(network)
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
        return self.version_setter(model_dict)

    def no_login_collect(self, source):
        asn_data = self.get_field(self.asn_pattern_n, source)
        company_data = self.get_field(self.company_pattern_n, source)
        model_dict = deepcopy(DATA_FORMAT)
        model_dict["region"] = self.get_field(self.region_pattern_n, source)
        model_dict["country"]["code"] = self.get_field(
            self.country_code_pattern_n, source
        )
        model_dict["latitude"] = self.get_field(self.latitude_pattern_n, source)
        model_dict["longitude"] = self.get_field(self.longitude_pattern_n, source)

        model_dict["isp"]["name"] = self.get_field(self.name_pattern_n, asn_data)
        model_dict["ip_network"] = self.get_field(self.ip_network_pattern_n, asn_data)
        model_dict["organization"] = self.get_field(self.name_pattern_n, company_data)
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
            model_dict["ip_network"]
        )
        country_code = model_dict["country"].get("code")
        if country_code is not None:
            model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
            model_dict["country"]["code"] = country_code
        else:
            model_dict["country"]["name"] = None
            model_dict["country"]["code"] = None
        return self.version_setter(model_dict)

    def login_collect(self, source):
        model_dict = deepcopy(DATA_FORMAT)
        model_dict["city"] = self.get_field(self.city_pattern, source)
        model_dict["region"] = self.get_field(self.region_pattern, source)
        model_dict["country"]["code"] = self.get_field(self.country_code_pattern, source)
        model_dict["latitude"] = self.get_field(self.latitude_pattern, source)
        model_dict["longitude"] = self.get_field(self.longitude_pattern, source)
        model_dict["ip_network"] = self.get_field(self.ip_network_pattern, source)
        model_dict["organization"] = self.get_field(self.organization_pattern, source)
        model_dict["isp"]["name"] = self.get_field(self.organization_pattern, source)
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
            model_dict["ip_network"]
        )
        country_code = model_dict["country"].get("code")
        if country_code is not None:
            model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(country_code)
            model_dict["country"]["code"] = country_code
        else:
            model_dict["country"]["name"] = None
            model_dict["country"]["code"] = None
        return self.version_setter(model_dict)


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
                    if "country" in elem.text.casefold():
                        try:
                            _, country = elem.text.split(": ")
                        except ValueError:
                            _, country = elem.text.split(":")
                        dict_data["country_code"] = country.strip()
                    elif "netname" in elem.text.casefold():
                        try:
                            _, isp = elem.text.split(": ")
                        except ValueError:
                            _, isp = elem.text.split(":")
                        dict_data["isp_name"] = isp.strip()
                except:
                    pass
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
        model_dict["version"] = self._get_version_network(network)

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

        return self.version_setter(model_dict)


class RipeCollector(BaseCollector):
    def login_collect(self, source):
        pass

    def no_login_collect(self, source):
        pass

    def no_login_api_collect(self, source):
        model_dict = deepcopy(DATA_FORMAT)
        try:
            source = source["objects"]["object"]
        except KeyError:
            return model_dict
        for data_fields in source:
            if data_fields.get("type") == "inetnum":
                try:
                    source = data_fields.get("attributes").get("attribute")
                except AttributeError:
                    return model_dict
                for item in source:
                    if item.get("name") == "country":
                        country_code = item.get("value")
                        model_dict["country"]["code"] = item.get("value")
                        model_dict["country"]["name"] = COUNTRY_CODE_MAPPER.get(
                            country_code
                        )
                    elif item.get("name") == "mnt-by":
                        model_dict["isp"]["name"] = item.get("value")
                    elif item.get("name") == "geoloc":
                        location = item.get("value").split(" -")
                        model_dict["longitude"] = location[0]
                        model_dict["latitude"] = location[1]
                    elif item.get("name") == "netname":
                        model_dict["organization"] = item.get("value")
                    elif item.get("name") == "inetnum":
                        ip_range = item.get("value").split(" - ")
                        model_dict["ip_from"] = str(
                            int(ipaddress.ip_address(ip_range[0]))
                        )
                        model_dict["ip_to"] = str(
                            int(ipaddress.ip_address(ip_range[1]))
                        )
            elif data_fields.get("type") == "route":
                try:
                    source_routes = data_fields.get("attributes").get("attribute")
                except AttributeError:
                    source_routes = None

                if source_routes is not None:
                    for item in source_routes:
                        if item.get("name") == "route":
                            model_dict["ip_network"] = item.get("value")
                            break
        return self.version_setter(model_dict)
