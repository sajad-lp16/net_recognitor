import re
import json
import ipaddress
from copy import deepcopy
from bs4 import BeautifulSoup

from ip_manager.utils.data_format import DATA_FORMAT, COUNTRY_CODE_MAPPER


class BaseCollector:
    def login_collect(self, source):
        raise NotImplementedError

    def no_login_collect(self, source):
        raise NotImplementedError

    @staticmethod
    def _get_ip_range(network):
        if network is None:
            return None, None
        network_obj = ipaddress.ip_network(network)
        return str(network_obj.network_address), str(network_obj.broadcast_address)

    @staticmethod
    def _ip_to_int(ip):
        try:
            return int(ipaddress.ip_address(ip))
        except:
            return None

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
        model_dict["ip_from"] = self._ip_to_int(model_dict["ip_from"])
        model_dict["ip_to"] = self._ip_to_int(model_dict["ip_to"])
        return model_dict

    @staticmethod
    def get_field(pat, target):
        if target is None:
            return
        data = re.findall(pat, target, re.I)
        if data:
            return data[0]


class IPInfoCollector(BaseCollector):
    def __init__(self):

        # no login patterns --------------------------------------------------------------------------------------------
        self.city_pattern_n_login = r'\n*city:\n*"([^"]+)"'
        self.region_pattern_n_login = r'\n*region:\s*\n"([^"]+)"'
        self.location_pattern_n_login = r'\n*loc:\n\s*"([^"]+)"'
        self.country_pattern_n_login = r'\n*country:\s*\n"([^"]+)"'
        self.org_pattern_n_login = r'\n*org:\s*\n"([^"]+)"'
        self.network_pattern_n_login = r'\n*network:\s*\n"([^"]+)"'
        self.address_pattern_n_login = r'\n*address:\s*\n"([^"]+)"'
        self.isp_name_pattern_n_login = r'\nname:\s*\n"([^"]+)"'

        # login patterns --------------------------------------------------------------------------------------------
        self.city_pattern = r'\n*city:*\n*"([^"]+)"'
        self.region_pattern = r'\n*region:*\s*\n"([^"]+)"'
        self.location_pattern = r'\n*loc:*\n\s*"([^"]+)"'
        self.country_pattern = r'\n*country:*\s*\n"([^"]+)"'
        self.org_pattern = r'\n*org:*\s*\n"([^"]+)"'
        self.network_pattern = r'\n*network:*\s*\n"([^"]+)"'
        self.address_pattern = r'\n*address:*\s*\n"([^"]+)"'
        self.isp_name_pattern = r'\nname:*\s*\n"([^"]+)"'

    @staticmethod
    def _extract_field(pat, source):
        try:
            return re.findall(pat, source)[0]
        except IndexError:
            return

    def login_collect(self, source):
        model_dict = deepcopy(DATA_FORMAT)
        location_data = self._extract_field(self.location_pattern, source)
        ip_network = self._extract_field(self.network_pattern, source)
        country_code = self._extract_field(self.country_pattern, source)
        country_name = COUNTRY_CODE_MAPPER.get(country_code)

        model_dict["isp"] = {"name": self._extract_field(self.isp_name_pattern, source)}
        model_dict["city"] = self._extract_field(self.city_pattern, source)
        model_dict["region"] = self._extract_field(self.region_pattern, source)
        model_dict["ip_network"] = ip_network
        model_dict["version"] = self._get_version_network(ip_network)
        model_dict["country"] = {
            "name": country_name,
            "code": country_code,
        }
        model_dict["organization"] = self._extract_field(self.org_pattern, source)
        model_dict["address"] = self._extract_field(self.address_pattern, source)
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(ip_network)
        if location_data is not None:
            model_dict["longitude"] = location_data.split(",")[0]
            model_dict["latitude"] = location_data.split(",")[1]

        return self.version_setter(model_dict)

    def no_login_collect(self, source):

        model_dict = deepcopy(DATA_FORMAT)
        location_data = self._extract_field(self.location_pattern_n_login, source)
        ip_network = self._extract_field(self.network_pattern_n_login, source)
        country_code = self._extract_field(self.country_pattern_n_login, source)
        country_name = COUNTRY_CODE_MAPPER.get(country_code)

        model_dict["isp"] = {
            "name": self._extract_field(self.isp_name_pattern_n_login, source)
        }
        model_dict["city"] = self._extract_field(self.city_pattern_n_login, source)
        model_dict["region"] = self._extract_field(self.region_pattern_n_login, source)
        model_dict["ip_network"] = ip_network
        model_dict["version"] = self._get_version_network(ip_network)
        model_dict["country"] = {
            "name": country_name,
            "code": country_code,
        }
        model_dict["organization"] = self._extract_field(
            self.org_pattern_n_login, source
        )
        model_dict["address"] = self._extract_field(
            self.address_pattern_n_login, source
        )
        model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(ip_network)
        if location_data is not None:
            model_dict["longitude"] = location_data.split(",")[0]
            model_dict["latitude"] = location_data.split(",")[1]

        return self.version_setter(model_dict)


class IPDataCollector(BaseCollector):
    def __init__(self):

        self.city_pattern = r"\n*CITY\n([^\n]+)\n"
        self.region_pattern = r"\n*REGION NAME\n([^\n]+)\n"
        self.country_code_pattern = r"\n*COUNTRY CODE\n([^\n]+)\n"
        self.latitude_pattern = r"\n*LATITUDE\n([^\n]+)\n"
        self.longitude_pattern = r"\n*LONGITUDE\n([^\n]+)\n"
        self.organization_pattern = r"\n*ORGANIZATION\n([^\n]+)\n"
        self.ip_network_pattern = r"\n*ROUTE\n([^\n]+)\n"

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
        model_dict["country"]["code"] = self.get_field(
            self.country_code_pattern, source
        )
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

    def no_login_collect(self, source):
        pass


class RipeCollector(BaseCollector):
    def __init__(self):

        # no login patterns --------------------------------------------------------------------------------------------
        self.isp_pattern_n_login = r"\n*netname:\s*([^\n]+)\n*"
        self.organization_pattern_n_login = r"\n*descr:\s*([^\n]+)\n*"
        self.country_pattern_n_login = r"\n*country:\s*([^\n#\s]+)\n*"
        self.route_pattern_n_login = r"\n*route:\s*([^\n]+)\n*"
        self.ip_range_pattern_n_login = r"\n*inetnum:\s*([^\n]+)\n*"

        self.ip_pattern = r"\s*([^\s-]+)\s*"

    def get_ips_from_text(self, net_range):
        ips = re.findall(self.ip_pattern, net_range)
        if not ips:
            return None, None
        return ips

    def login_collect(self, source):
        return self.no_login_collect(source)

    def no_login_collect(self, source):
        model_dict = deepcopy(DATA_FORMAT)
        model_dict["isp"]["name"] = self.get_field(self.isp_pattern_n_login, source)
        model_dict["organization"] = self.get_field(
            self.organization_pattern_n_login, source
        )
        country_code = self.get_field(self.country_pattern_n_login, source)
        self.set_country(model_dict, {"country_code": country_code})
        network = self.get_field(self.route_pattern_n_login, source)
        model_dict["ip_network"] = network
        if network is not None:
            model_dict["ip_from"], model_dict["ip_to"] = self._get_ip_range(
                model_dict["ip_network"]
            )
        else:
            net_range = self.get_field(self.ip_range_pattern_n_login, source)
            if net_range:
                model_dict["ip_from"], model_dict["ip_to"] = self.get_ips_from_text(
                    net_range
                )
        return self.version_setter(model_dict)

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
                        model_dict["ip_from"] = str(ipaddress.ip_address(ip_range[0]))
                        model_dict["ip_to"] = str(ipaddress.ip_address(ip_range[1]))
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
