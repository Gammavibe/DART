from WebIo import *

class DartIo(Get):

    def read(self, **params):
        params.update(crtfc_key=self.crtfc_key)
        resp=super().read(**params)
        return resp

    @property
    def crtfc_key(self):
        return '492df870d01789026922a68e24708f1c2c532c5b'

    @crtfc_key.setter
    def crtfc_key(self,crtfc_key):
        self.__crtfc_key=crtfc_key

#각문서를 실행하는 클래스
#문서별로 loop를 돌면서 문서를 실행.
#수신된 문서 텍스트에서 검색 결과가 True인지를 반환
#View for retreiving text contents not Requests but with HTML Session
#class DartView(Get_View):
#    def read(self, **params):
#        resp=super().read(**params)
#        return resp
