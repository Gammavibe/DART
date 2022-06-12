from DartIo import *
from KindIo import *

# 홑밑줄(single underscore) : 보통 내부적으로 사용하는 변수일 때 사용합니다.
# 곁밑줄(double underscore) : 클래스 외부에서 접근할 수 없도록 내부 변수로 만듭니다.

class DartList(DartIo):

    def fetch(self, bgn_de, pblntf_ty, end_de=None, page_count='100', corp_cls=None, page_no=None, last_reprt_at='Y'):
        resp = super().read(bgn_de=bgn_de, end_de=end_de, pblntf_ty=pblntf_ty, page_count=page_count, corp_cls=corp_cls,
                            page_no=page_no, last_reprt_at=last_reprt_at)
        return resp.json()

    @property
    def url(self):
        return 'https://opendart.fss.or.kr/api/list.json'

class KindList(KindIo):

    def fetch(self, fromDate, toDate=None, method='searchDetailsSub', forward='details_sub', currentPageSize='100', pageIndex='1', orderMode='1', securities='1', lastReport='T', orderStat='D',repIsuSrtCd=''):
        '''this method will retrieve whole list of reports for specific period '''
        if toDate is None:
            toDate=fromDate
        resp = super().read(fromDate=fromDate, toDate=toDate, method=method, forward=forward, currentPageSize=currentPageSize,
                            pageIndex=pageIndex, orderMode=orderMode, securities=securities, lastReport=lastReport, orderStat=orderStat, repIsuSrtCd=repIsuSrtCd)
        return resp

    def fetch_kwd(self, fromDate, toDate=None, filter_kwg=None, pageIndex='1'):
        '''this method will retrieve data for specific topic such as self-trading shares with keyword 자기주식매매'''
        if toDate is None:
            toDate=fromDate
        resp = super().read(fromDate=fromDate, toDate=toDate, method='searchDetailsSub', forward='details_sub', currentPageSize='100',
                            pageIndex=pageIndex, orderMode='1', lastReport='T', orderStat='D', repIsuSrtCd='', bfrDsclsTyp='on', reportNm=filter_kwg, reportNmTemp=filter_kwg)
        return resp

    @property
    def url(self):
        return 'https://kind.krx.co.kr/disclosure/details.do'

class KindListToday(KindIo):

    def fetch(self, selDate, method='searchTodayDisclosureSub', forward='todaydisclosure_sub', currentPageSize='100', pageIndex='1', orderMode='0', orderStat='D', todayFlag='Y', chose='S'):
        resp = super().read(selDate=selDate, method=method, forward=forward, currentPageSize=currentPageSize,
                            pageIndex=pageIndex, orderMode=orderMode, orderStat=orderStat,
                            todayFlag=todayFlag, chose=chose)

        return resp

    @property
    def url(self):
        return 'https://kind.krx.co.kr/disclosure/todaydisclosure.do'


class HyslrSttus(DartIo):

    def fetch(self, corp_code, bsns_year, reprt_code):
        resp = super().read(corp_code=corp_code, bsns_year=bsns_year, reprt_code=reprt_code)
        return resp.json()

    @property
    def url(self):
        return 'https://opendart.fss.or.kr/api/hyslrSttus.json'


class DartViewer(Get_View):

    def fetch(self, rcpNo):
        resp = super().read(rcpNo=rcpNo)
        return resp

    @property
    def url(self):
        return 'https://dart.fss.or.kr/dsaf001/main.do'

class KindViewer(Get_View):

    def fetch(self, acptno, method='search'):
        resp = super().read(acptno=acptno, method=method)
        return resp

    @property
    def url(self):
        return 'https://kind.krx.co.kr/common/disclsviewer.do'