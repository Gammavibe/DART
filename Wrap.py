from Core import *
from datetime import datetime, timedelta
import pandas as pd
import time
import re
from bs4 import BeautifulSoup as bs

# 렌더링하여 문서 내용을 검색하기 위한 전문을 받는 다운로더
class DartDownloader(DartViewer):
    def __init__(self):
        super().__init__()
        #self.brwsr=DartViewer()
        #self.rqst=requests.session()

        self.subUrl='https://dart.fss.or.kr/report/viewer.do'

    def get_docs_params(self, rcpNo):
        #resp=self.brwsr.fetch(rcpNo)
        resp=self.fetch(rcpNo)
        resp.html.render(sleep=1)
        attr=resp.html.lxml.get_element_by_id('ifrm').attrib.get('src')
        splt = [x.split('=') for x in attr.split('?')[1].split('&')]
        q_dict={}
        for q in splt:
            q_dict[q[0]]=q[1]
        q_dict['offset']='0'
        q_dict['length'] = '0'
        #resp.session.params.update(q_dict)
        #url='https://dart.fss.or.kr/report/viewer.do'
        #resp=resp.session.get(url)
        #return resp.text
        #resp.session.close()
        return q_dict

    def get_html(self, rcpNo):
        params=self.get_docs_params(rcpNo)
        resp=self.read(url=self.subUrl, params=params)
        return resp.text

class KindDownloader(KindViewer):
    def __init__(self):
        super().__init__()
        #self.subUrl='https://kind.krx.co.kr/common/disclsviewer.do'

    def get_doc_No(self, acptno):
        try:
            resp=self.read(acptno=acptno, method='search')
        except Exception as e:
            print(e)
        else:
            soup=bs(resp.text, 'html.parser')
            docNo=soup.find('option', attrs={'value':re.compile('[0-9]+\|Y')}).get_attribute_list('value')[0]
            docNo=docNo.replace('|Y','')
            return docNo

    def get_doc_url(self, acptno):
        docNo=self.get_doc_No(acptno)
        try:
            resp=self.read(docNo=docNo, method='searchContents')
        except Exception as e:
            print(e)
        else:
            url=re.search(',\'https:([0-9A-z-./])+',resp.text).group(0).replace(',\'','')
            return url

    def get_html(self, acptno):
        url=self.get_doc_url(acptno)
        resp=requests.get(url)
        resp.encoding='UTF-8'
        return resp.text

def get_dart_list(bgn_de, end_de=None, pblntf_ty=None, filter_kwg=None):
    #pblntf_ty=공시유형
    # A : 정기공시
    # B : 주요사항보고
    # C : 발행공시
    # D : 지분공시
    # E : 기타공시
    # F : 외부감사관련
    # G : 펀드공시
    # H : 자산유동화
    # I : 거래소공시
    # j : 공정위공시
    # : All
    if end_de is None:
        end_de=bgn_de
    dt=spltDtList(bgn_de, end_de)
    df=pd.DataFrame()
    for d in dt:
        try:
            resp=DartList().fetch(bgn_de=d[0], end_de=d[1], pblntf_ty=pblntf_ty)
            if resp['status']=='013':
                raise FileNotFoundError
            elif resp['status']=='000':
                df = pd.concat([df, pd.DataFrame(resp['list'])])
                pg_cnt=resp['total_page']
        except Exception as e:
            raise e

        if pg_cnt > 1 :
                for i in range(2,resp['total_page']+1):

                    #print(d, i)
                    resp = DartList().fetch(bgn_de=d[0], end_de=d[1], pblntf_ty=pblntf_ty, page_no=i)
                    df = pd.concat([df, pd.DataFrame(resp['list'])])
                    time.sleep(1)

    if filter_kwg is None :
        pass
    else:
        idx=df['report_nm'].str.contains(filter_kwg)
        df=df[idx]

    df.reset_index(drop=True, inplace=True)
    return df

def get_kind_list(bgn_de, end_de=None, filter_kwg=None):
    '''Outside this method, resp should be retrieved
    This method only handle to transform resp from raw data to DataFrame'''
    if end_de is None:
        end_de=bgn_de
    dt=spltDtList(bgn_de, end_de)
    df=pd.DataFrame()
    for d in dt:
        try:
            resp=KindList().fetch(fromDate=d[0], toDate=d[1])
            xmlText=resp.text
        except Exception as e:
            raise e
        soup=bs(xmlText, 'html.parser')
        xmlInfo=soup.find('div', 'info type-00')
        df=get_kind_list_df(xmlText)
        pg_cnt=int(re.search('/\d+',xmlInfo.text).group(0).replace('/',''))

        if pg_cnt > 1 :
            for i in range(2,pg_cnt+1):

                #print(d, i)
                resp = KindList().fetch(fromDate=d[0], toDate=d[1], pageIndex=i)
                dfTemp=get_kind_list_df(resp.text)
                df = pd.concat([df, dfTemp])
                time.sleep(2)

    if filter_kwg is None :
        pass
    else:
        idx=df['report_nm'].str.contains(filter_kwg)
        df=df[idx]

    df.reset_index(drop=True, inplace=True)
    return df

def get_html_tables(resp):
    '''Get Table from KIND html with beautifulsoup looking for Tbody'''
    soup=bs(resp, 'html.parser')
    tbody=soup.find_all('tbody')
    table_list=list()
    for t in tbody:

        subRows=t.find_all('tr')
        cntRows=len(subRows)
        #1행짜리 테이블은 1열이 Head, 2열이 Value
        if cntRows==1:
            df=pd.DataFrame()
            df=df.append({subRows[0].find_all('td')[0].text:subRows[0].find_all('td')[1].text},ignore_index=True)
            table_list.append(df)
        else:
            #column name should be stripped
            colHead=[cols.text for cols in subRows[0].find_all('td')]
            #cntCols=len(colHead)
            df=pd.DataFrame(columns=colHead)

            for i in range(1,cntRows):
                colVals=[cols.text for cols in subRows[i].find_all('td')]
                valRows=dict(zip(colHead,colVals))
                df = df.append(valRows,ignore_index=True)
            table_list.append(df)

    return table_list



#테이블만 HTML에서 추려서 리스트에 넣는다
#테이블을 순환하면서 어떤 테이블인지 확인
def get_kind_kwd_list(bgn_de, end_de=None, filter_kwg=None):

    if end_de is None:
        end_de=bgn_de
    dt=spltDtList(bgn_de, end_de, 1000)
    df=pd.DataFrame()
    for d in dt:
        try:
            resp=KindList().fetch_kwd(fromDate=d[0], toDate=d[1], filter_kwg=filter_kwg)
            xmlText=resp.text
        except Exception as e:
            raise e
        soup=bs(xmlText, 'html.parser')
        xmlInfo=soup.find('div', 'info type-00')
        df=get_kind_list_df(xmlText)
        pg_cnt=int(re.search('/\d+',xmlInfo.text).group(0).replace('/',''))

        if pg_cnt > 1 :
            for i in range(2,pg_cnt+1):

                #print(d, i)
                resp = KindList().fetch_kwd(fromDate=d[0], toDate=d[1], filter_kwg=filter_kwg, pageIndex=i)
                dfTemp=get_kind_list_df(resp.text)
                df = pd.concat([df, dfTemp])
                time.sleep(1)

    df.reset_index(drop=True, inplace=True)
    return df

def get_kind_list_df(xmlText):
    soup=bs(xmlText, 'html.parser')
    xmlList=soup.find_all('tr')
    i=1
    colHead=['corp_code', 'corp_name', 'stock_code', 'corp_cls', 'report_nm', 'rcept_no', 'flr_nm', 'rcept_dt', 'rm']
    df=pd.DataFrame(columns=colHead)

    for i in range(1,len(xmlList)):
        stockInfo=xmlList[i].find_all('td')
        corp_name=stockInfo[2].text.strip()
        print(i)
        try:
        #안됨
            corp_cls=stockInfo[2].find('img').get_attribute_list('alt')[0]
        except Exception as e:
            corp_cls=None
            stock_code=None
        else:
            #주권일 경우에만 종목코드가 있음
            #상장폐지종목은
            stock_code=re.search('companysummary_open\(\'\w+',str(stockInfo[2])).group(0).replace('companysummary_open(\'','')
        finally:
            report_nm=stockInfo[3].text.strip()
            flr_nm=stockInfo[4].text.strip()
            rcept_no=re.search('openDisclsViewer\(\'\d+',str(stockInfo[3])).group(0).replace('openDisclsViewer(\'','')
            #ETF같은 경우 STCK코드가 없을 수 있음
            rcept_dt=datetime.strptime(stockInfo[1].text,'%Y-%m-%d %H:%M').strftime('%Y%m%d')
            df=df.append({'corp_name':corp_name, 'stock_code':stock_code, 'corp_cls':corp_cls, 'report_nm':report_nm,'rcept_no':rcept_no, 'flr_nm':flr_nm, 'rcept_dt':rcept_dt, 'rm':'kind'}, ignore_index=True)
            #df['stock_code']=df['stock_code']+'0'
    return df



def find_kwd_docs(str, kwd):
    if kwd in str:
        return True
    else:
        return False

def spltDtList(bgn_de, end_de, interval=None):
        if interval is None:
            interval=90
        bgn = datetime.strptime(bgn_de, '%Y%m%d')
        end = datetime.strptime(end_de, '%Y%m%d')
        date_diff=end-bgn

        if date_diff.days<=interval :
            return [[bgn_de, end_de]]
        else:
            date_list = list()
            divcnt=date_diff.days//interval
            end=bgn-timedelta(days=1)

            for i in range(0, divcnt):
                bgn = end + timedelta(days=1)
                end = bgn + timedelta(days=interval-1)
                bgn_tmp = datetime.strftime(bgn, '%Y%m%d')
                end_tmp = datetime.strftime(end, '%Y%m%d')

                date_list.append([bgn_tmp,end_tmp])

            bgn = end + timedelta(days=1)
            bgn_de = datetime.strftime(bgn, '%Y%m%d')
            date_list.append([bgn_de, end_de])
            return date_list

def getDartUrl(rcept_no):
    url='https://dart.fss.or.kr/dsaf001/main.do?rcpNo=' + rcept_no
    return url

def getKindUrl(acptno):
    url='https://kind.krx.co.kr/common/disclsviewer.do?method=search&acptno=' + acptno
    return url