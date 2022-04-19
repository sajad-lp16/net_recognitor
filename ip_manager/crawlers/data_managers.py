from ip_manager import models
from ip_manager.utils import functions, data_format

from . import data_collectors


class BaseDataManager:
    def login_manager(self, source):
        raise NotImplementedError

    def no_login_manager(self, source):
        raise NotImplementedError

    @staticmethod
    def manage(data, source_name):
        if data_format.DATA_FORMAT == data:
            return
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
        try:
            source = models.SourcePool.objects.get(name=source_name)
        except models.SourcePool.DoesNotExist:
            functions.add_initial_sources()
            source = models.SourcePool.objects.get(name=source_name)
        try:
            return models.IpRange.objects.create(
                source=source, country=country, isp_id=isp_id, **data
            )
        except:
            return


class IPInfoManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.IPInfoCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ipinfo")

    def no_login_manager(self, source):
        pass


class IPDataManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.IPDataCollector()


    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ipdata")


    def login_api_manager(self, source):
        data = self.collector.login_api_collect(source)
        return self.manage(data, "ipdata")

    def no_login_manager(self, source):
        data = self.collector.no_login_collect(source)
        return self.manage(data, "ipdata")


class MyIPManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.MyIPCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "myip")

    def no_login_manager(self, source):
        pass


class RipeManager(BaseDataManager):
    def __init__(self):
        self.collector = data_collectors.RipeCollector()

    def login_manager(self, source):
        data = self.collector.login_collect(source)
        return self.manage(data, "ripe")

    def no_login_api_manager(self, source):
        data = self.collector.no_login_api_collect(source)
        return self.manage(data, "ripe")

    def no_login_manager(self, source):
        data = self.collector.no_login_collect(source)
        return self.manage(data, "ripe")
