from ip_manager import models
from . import data_collectors


class BaseDataManager:
    @staticmethod
    def manage(data, source_name):
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
        source = models.SourcePool.objects.get(name=source_name)
        return models.IpRange.objects.create(
            source=source, country=country, isp_id=isp_id, **data
        )


class IPInfoManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.IPInfoCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ipinfo")


class IPDataManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.IPDataCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ipdata")


class MyIPManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.MyIPCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "myip")


class RipeManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.RipeCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ripe")
