from WebIo import *

class KindIo(Post):

    def read(self, **params):
        #self.headers.update({'referer': 'https://kind.krx.co.kr/disclosure/details.do?method=searchDetailsMain'})
        resp=super().read(**params)
        return resp
    """
    'referer': 'https://kind.krx.co.kr/disclosure/todaydisclosure.do'
    method: searchTodayDisclosureSub
    currentPageSize: 100
    pageIndex: 1
    orderMode: 0
    orderStat: D
    marketType: 
    forward: todaydisclosure_sub
    searchMode: 
    searchCodeType: 
    chose: S
    todayFlag: Y
    repIsuSrtCd: 
    selDate: 2022-04-26
    searchCorpName: 
    """