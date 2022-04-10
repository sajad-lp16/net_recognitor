import re
import json
import ipaddress
from copy import deepcopy

from ip_manager.utils.data_format import DATA_FORMAT


def collect_ip_info(source):
    def _extract_field(pat):
        return json.loads(re.findall(pat, source)[0])

    def _collect_ip_from_to(network):
        ip_ranges = tuple(ipaddress.ip_network(network).hosts())
        return ip_ranges[0], ip_ranges[-1]

    data = deepcopy(DATA_FORMAT)

    city_pattern = r'city: (.*)\n'
    region_pattern = r'region: (.*)\n'
    location_pattern = r'loc: (.*)\n'
    country_pattern = r'country: (.*)\n'
    org_pattern = r'org: (.*)\n'
    network_pattern = r'network: (.*)\n'
    address_pattern = r'address: (.*)\n'
    isp_name_pattern = r'\bname: (.*)\n'

    location_data = _extract_field(location_pattern)
    ip_network = _extract_field(network_pattern)

    data['isp'] = {'name': _extract_field(isp_name_pattern)}
    data['city'] = _extract_field(city_pattern)
    data['region'] = _extract_field(region_pattern)
    data['ip_network'] = ip_network
    data['country'] = {'name': _extract_field(country_pattern)}
    data['organization'] = _extract_field(org_pattern)
    data['address'] = _extract_field(address_pattern)
    data['longitude'] = location_data.split(',')[0]
    data['latitude'] = location_data.split(',')[1]
    data['ip_from'], data['ip_to'] = _collect_ip_from_to(ip_network)

    return data
