from copy import deepcopy

from ip_manager import models
from . import data_collectors


def ip_info_manager(source):
    data = data_collectors.collect_ip_info(source)
    country = None
    isp = None
    try:
        country_code = data.get('country').get('code')
    except AttributeError:
        country_code = None
    finally:
        data.pop('country')
    try:
        name = data.get('isp').get('name')
    except AttributeError:
        name = None
    finally:
        data.pop('isp')

    if country_code is not None:
        country = models.Country.objects.get_or_create(country_code)
    if name is not None:
        isp = models.ISP.objects.get_or_create(name=data.get('isp').get('name'))
    return models.IpRange.objects.create(
        country=country,
        isp=isp,
        **data
    )
