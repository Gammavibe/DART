import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['C:\\Users\\KoreaUniv\\PycharmProjects\\KRX', 'C:\\Users\\KoreaUniv\\PycharmProjects\\DART', 'C:\\Users\\KoreaUniv\\Anaconda3\\envs\\DG\\Lib\\site-packages\\pykrx', 'C:\\Users\\KoreaUniv\\PycharmProjects\\TelegramBot'])

from Wrap import *
from pyTelegram import *
import time
import numpy as np

import threading
import multiprocessing

# MULTIPROCESSING VS. THREADING IN PYTHON:
# https://timber.io/blog/multiprocessing-vs-multithreading
# # --------------------------------------------------------------------------in-python-what-you-need-to-know/

# 내용:
#    1. 우선 모든 다트 공시내용을 받는다
#    2. 현재 큐에 공시들이 들어가 있는지 확인한다
#    3. 새로운 공시만 필터링한다
#    4. 관심종목에 있는 종목들을 큐에 넣는다
#    5. 관심종목이 아닌 종목은 문서를 열고 관심종목명이 내용에 있는지 확인한다
#    6. 있으면 3 항목도 큐에 넣는다
#    7. 큐에 새로운 항목들을 알림한다
#    8. 다시 1로 반복

if __name__ == "__main__":

    BOT=MSGBOT('')
    user=''
    # bgn_de = '20220418'
    # end_de = '20220311'
    # filter_kwg = '주주총회소집공고'
    # kwd = '분기배당'
    # dartList=get_dart_list(bgn_de, end_de, 'E', filter_kwg)
    # dartList = get_dart_list(bgn_de, end_de, 'E')
    # dartList = get_dart_list(bgn_de, end_de)

    colHead=['corp_code', 'corp_name', 'stock_code', 'corp_cls', 'report_nm', 'rcept_no', 'flr_nm', 'rcept_dt', 'rm']
    ReportQueue=pd.DataFrame(columns=colHead)
    ReportPrev=pd.DataFrame(columns=colHead)
    MonitoringList=pd.read_excel('C:\\Users\\KoreaUniv\\Desktop\\작업\\MntList.xls')
    MonitoringList['isu_cd']=MonitoringList['isu_cd'].astype('str').str.zfill(6)
    MonitoringCode=MonitoringList['isu_cd'].to_list()

    bMonitoringKwd=MonitoringList['flag_kwd']==True
    MonitoringKwd=MonitoringList.loc[bMonitoringKwd, 'isu_nm'].to_list()

    ReportQueue['flag_sent']=None

    bFlag=True
    while bFlag:
        bgn_de=datetime.now().strftime('%Y%m%d')
        try:
            #당일 내용이 0개이면 오류남 수정 필요
            dartList = get_dart_list(bgn_de)
#            print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' Total #: ' + str(dartList.shape[0]))
        except Exception as e:
            #pass
            print(type(e))

        else:
            bInKSEKDQ=dartList['corp_cls'].isin(['Y','K'])
            #새로 추가된 종목만 추리기
            bIsIncluded=dartList['rcept_no'].isin(ReportPrev['rcept_no'])
            bTargetCorp= bInKSEKDQ & ~bIsIncluded
            ReportTemp=dartList[bTargetCorp]

            #모니터링 종목은 일단 큐에 추가하기
            bIsMonitoringMemb=ReportTemp['stock_code'].isin(MonitoringList['isu_cd'])
            bIsSecDocs=ReportTemp['report_nm'].str.contains('|'.join(['일괄신고추가서류', '증권발행실적보고서','투자설명서']))
            bFiltered= bIsMonitoringMemb & ~bIsSecDocs
            bFilteredKwd= ~bIsMonitoringMemb & ~bIsSecDocs
            ReportQueue=pd.DataFrame.append(ReportQueue, ReportTemp[bFiltered], ignore_index=True)

            #모니터링 종목이 아닌 경우 보고서 내용에 모니터링 종목 키워드가 있는지 확인
            #있으면 큐에 추가
            #[kwd in str for kwd in MonitoringList['isu_nm']] 창의적인 키워드 검색 방법
            ReportToCheck=ReportTemp[bFilteredKwd]
            ReportToCheck=ReportToCheck.reset_index(drop=True)
            ReportToCheck['FIND']=None
            CntCheckList=ReportQueue.shape[0]
            #reader=DartDownloader()
            print('To check #: ' + str(CntCheckList))
            if CntCheckList>0:
                for i in range(CntCheckList):
                    try:
                        reader=DartDownloader()
                        ReportToCheck.loc[i, 'HTML'] = reader.get_html(ReportQueue.loc[i, 'rcept_no'])
                        del reader

                        #time.sleep(1)

                    except Exception as e:
                        print(e)
                        #dartList에서 삭제
                        #Load 실패시 다음 조회 루프에서 재조회하기 위함
                        #dartList[dartList['recpt_no']==ReportToCheck.loc[i, 'rcept_no']].drop(i)



                #HTML without DROP causes Rendering contents when toClipboard
                ReportToCheck.drop('HTML', inplace=True, axis=1)
                bWithKwd=~ReportToCheck['FIND'].isnull()
                ReportQueue=pd.DataFrame.append(ReportQueue, ReportToCheck[bWithKwd], ignore_index=True)

            cntReportQueue=ReportQueue.shape[0]
            print('Current Queue #: ' + str(cntReportQueue))
            cntNew=0
            #큐를 순환하면서 텔레그렘으로 메시지 발송
            #읽음 플래그가 없으면 읽음 표시 후 발송
            #tmpQueue=ReportQueue
            #bFlagSent=tmpQueue['flag_sent']==True
            #bInMonitoring=tmpQueue['stock_code'].isin(MonitoringList['isu_cd'])
            bIsMonitoring=ReportQueue['stock_code'].isin(MonitoringList['isu_cd'])
            for i in range(cntReportQueue):
                reporter=''
                mkt_tp=''

                #(ReportQueue.loc[i,'flag_sent'] != True)
                if ReportQueue.loc[i,'flag_sent'] != True:
                    #Set Market Type
                    bIsMonitoring=ReportQueue['stock_code'].isin(MonitoringList['isu_cd'])
                    if bIsMonitoring.loc[i]:
                        #모니터링 리스트에는 있지만 마켓 타입이 없는 경우 필터링
                        #Df의 NaN은 !=np.nan이나 None으로 비교가 되지 않음. pd.notnull() 혹은 pd.isnull()로 비교할 것
                        #MKT TYPE이 부여된 경우
                        if ~MonitoringList.loc[MonitoringList['isu_cd']==ReportQueue.loc[i,'stock_code'], 'mkt_tp'].isnull().values[0]:
                            mkt_tp='(' + MonitoringList.loc[MonitoringList['isu_cd']==ReportQueue.loc[i,'stock_code'], 'mkt_tp'].values[0] + ')'
                        #키워드 검색으로 출력된 경우(애초에 MKT TYPE이 있었으면 키워드 검색까지 가지 않음)
                        elif pd.notnull(ReportQueue.loc[i,'FIND']):
                            mkt_tp='(' + ReportQueue.loc[i,'FIND'] + ')'
                        #MKT TYPE이 부여되지 않은 기타 모니터링 종목
                        else:
                            pass
                    #Set Reporter
                    bReporter=ReportQueue['flr_nm']!=ReportQueue['corp_name']
                    ReportQueue.loc[bReporter,'reporter']='보고자: ' + ReportQueue.loc[bReporter,'flr_nm'] + '\n'
                    #
                    if ReportQueue.loc[i,'flr_nm']!=ReportQueue.loc[i,'corp_name']:
                        reporter='보고자: ' + ReportQueue.loc[i,'flr_nm'] +'\n'
                    #send Telegram Messege
                    msg=ReportQueue.loc[i,'corp_name'] + mkt_tp + '\n' + reporter + ReportQueue.loc[i,'report_nm'] + '\n' + getDartUrl(ReportQueue.loc[i,'rcept_no'])
                    #if not pd.isnull(ReportQueue.loc[i,'FIND']):
                    #    msg=ReportQueue.loc[i,'FIND'] + '\n' + msg

                    BOT.bot.send_message(user, msg)
                    ReportQueue.loc[i,'flag_sent']=True
                    cntNew = cntNew+1


            #직전 전체 리스트는 보관 할 것
            ReportPrev=dartList

            print('Sent #: ' + str(cntNew) + ', Total #: ' + str(dartList.shape[0]) + '  ' + datetime.now().strftime('%m/%d %H:%M') + '\n')
            #print(str(datetime.now().strftime('%Y-%m-%d %H:%M')) + ' Total #: ' + str(dartList.shape[0]))
        #주말이거나 오후 7시30분이 넘으면 종료
        if datetime.today().weekday()>=5 or (time.localtime()[3]*60+30)>=1170 or (time.localtime()[3]<=6):
            print('CLOSED Now: '+ datetime.now().strftime('%Y-%m-%d %H:%M'))

            bFlag=False
            print(bFlag)
        time.sleep(20)



        # dartList['FIND']=dartList['rcept_no'].apply(run, args=(kwd,))



    #############Multiprocessing
    # with multiprocessing.Pool(2) as pool:
    #    data = pool.starmap(run, kwgs)
    #    print(data)
    #    df = pd.concat(data)

    #############Threading
    # threads = [threading.Thread(target=run, args=(x, kwd)) for x in df]
    # for thr in threads:
    #    thr.start()
    #for thr in threads:
    #    thr.join()
