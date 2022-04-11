from ip_manager import models
from . import data_collectors


def ip_info_manager(source):
    data = data_collectors.collect_ip_info(source)
    country = None
    isp_id = None
    try:
        country_code = data.get("country").get("code")
        country_name = data.get("country").get("name")
    except AttributeError:
        country_code = None
        country_name = None
    finally:
        data.pop("country")
    try:
        isp_name = data.get("isp").get("name")
    except AttributeError:
        isp_name = None
    finally:
        data.pop("isp")

    if country_code is not None:
        country, _ = models.Country.objects.get_or_create(
            name=country_name, code=country_code
        )
    if isp_name is not None:
        isp, _ = models.ISP.objects.get_or_create(name=isp_name)
        isp_id = isp.id
    source_id = models.SourcePool.objects.get(name="ipinfo").id
    return models.IpRange.objects.create(
        source_id=source_id, country=country, isp_id=isp_id, **data
    )
