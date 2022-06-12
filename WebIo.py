import requests
from requests_html import HTMLSession
from abc import abstractmethod


class Post():
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def read(self, **params):
        resp = requests.post(self.url, headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        raise NotImplementedError


class Get:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def read(self, **params):
        resp = requests.get(self.url, headers=self.headers, params=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        raise NotImplementedError


class Get_View:
    def __init__(self):
        self.s = HTMLSession()
        self.headers = {"User-Agent": "Mozilla/5.0"}
        #self.s.headers= {"User-Agent": "Mozilla/5.0"}

    def read(self, **params):
        self.s.params.update(**params)
        resp = self.s.get(self.url, timeout=2)
        return resp

    @property
    @abstractmethod
    def url(self):
        raise NotImplementedError

    def __del__(self):
        self.s.close()