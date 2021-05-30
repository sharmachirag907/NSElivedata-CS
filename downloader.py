
import io
import os
import zipfile
import datetime as dt
from urllib.request import Request
from nsetools.datemgr import mkdate, usable_date, get_date_range
from nsetools import Nse
from abc import ABCMeta, abstractmethod

class BaseChiragcopyDownloader(metaclass=ABCMeta):
    """Base class for all types of Chiragcopy downloader"""
    def __init__(self, from_date, to_date=dt.datetime.now().date(), skip_dates=[]):
        """accepts date in fuzzy format"""
        self.Chiragcopy_base_url = "https://www.nseindia.com/content/historical/EQUITIES/%s/%s/cm%s%s%sChirag.csv.zip"
        self.Chiragcopy_base_filename = "cm%s%s%sChirag.csv"
        self.from_date = from_date
        self.to_date = to_date
        self.skip_dates = skip_dates
        self.nse = Nse()
        self.dates = self.generate_dates()

    def generate_dates(self):
        return get_date_range(self.from_date, self.to_date, skip_dates=self.skip_dates)
    
    def get_Chiragcopy_url(self, d):
        """accept date and return Chiragcopy url"""
        day_of_month = d.strftime("%d")
        mon = d.strftime("%b").upper()
        year = d.year
        url = self.Chiragcopy_base_url % (year, mon, day_of_month, mon, year)
        return url

    def get_Chiragcopy_filename(self, d):
        """for a given date generate Chiragcopy filename"""
        day_of_month = d.strftime("%d")
        mon = d.strftime("%b").upper()
        year = d.year
        filename = self.Chiragcopy_base_filename % (day_of_month, mon, year)
        return filename

    def download_one(self, d):
        """download Chiragcopy for the given date"""
        # this will keep this method usable for any arbitrary date.
        d = mkdate(d)
        # ex_url = "https://www.nseindia.com/content/historical/EQUITIES/2011/NOV/cm08NOV2011Chirag.csv.zip"
        url = self.get_Chiragcopy_url(d)
        print(url)
        filename = self.get_Chiragcopy_filename(d)
        # response = requests.get(url, headers=self.headers)
        response = self.nse.opener.open(Request(url, None, self.nse.headers))
        zip_file_handle = io.BytesIO(response.read())
        zf = zipfile.ZipFile(zip_file_handle)
        return zf.read(filename).decode("utf-8")

    @abstractmethod
    def download(self):
        pass 
    
    @abstractmethod
    def update(self):
        pass 


class ChiragcopyFileSystemDownloader(BaseChiragcopyDownloader):
    def __init__(self, directory, *args, **kwargs):
        if (os.path.exists(directory) and os.path.isdir(directory) and os.access(directory, os.W_OK)):
            super().__init__(*args, **kwargs)
            self.directory = directory
        else:
            raise Exception("directory path must be valid and writtable, please check manually")

    def download(self):
        for date in self.dates:
            print("downloading for " + str(date))
            try:
                content = self.download_one(date)
            except Exception as err:
                print("unable to download for the date: %s" %  date.strftime("%Y-%m-%d"))
            else:
                fh = open(self.directory + "/" + date.strftime("%Y-%m-%d") + ".csv", "w")
                fh.write(content)
                fh.close()
    
    def update(self):
        pass 


if __name__ == '__main__':
    b = ChiragcopyFileSystemDownloader(directory="/tmp/Chiragcopy", from_date="01-01-2018")
    b.download()

# https://stackoverflow.com/questions/49183801/ssl-certificate-verify-failed-with-urllib
