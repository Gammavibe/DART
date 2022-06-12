from Wrap import *


if __name__ == "__main__":
    kindList = get_kind_kwd_list('20200101','20220518','자기주식')
    kindList = get_kind_kwd_list('20220101','20220518','자기주식매매 체결내역')
    kindHandler = KindDownloader()

    colHead=['corp_code', 'corp_name', 'stock_code', 'corp_cls', 'report_nm', 'rcept_no', 'flr_nm', 'rcept_dt', 'rm']
    ReportQueue=pd.DataFrame(columns=colHead)

    MonitoringList=pd.read_excel('C:\\Users\\KoreaUniv\\Desktop\\작업\\MntList.xls')
    MonitoringList['isu_cd']=MonitoringList['isu_cd'].astype('str').str.zfill(6)
    MonitoringCode=MonitoringList['isu_cd'].to_list()


    bIsMonitoringMemb=kindList['stock_code'].isin(MonitoringList['isu_cd'])
    bIsSecDocs=kindList['report_nm'].str.contains('|'.join(['취득']))
    bIsExcluded=kindList['report_nm'].str.contains('|'.join(['결과','해지']))
    bFiltered= bIsMonitoringMemb & bIsSecDocs & ~bIsExcluded
    ReportQueue=pd.DataFrame.append(ReportQueue, kindList[bFiltered], ignore_index=True)

    CntCheckList=ReportQueue.shape[0]
    #reader=DartDownloader()
    print('To check #: ' + str(CntCheckList))
    if CntCheckList>0:
        for i in range(CntCheckList):
            try:
                reader=KindDownloader()
                ReportQueue.loc[i, 'HTML'] = reader.get_doc_url(ReportQueue.loc[i, 'rcept_no'])
                del reader

                #time.sleep(1)

            except Exception as e:
                print(e)
                #dartList에서 삭제
                #Load 실패시 다음 조회 루프에서 재조회하기 위함

