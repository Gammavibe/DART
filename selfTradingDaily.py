import pandas as pd

from wrap import *


if __name__ == "__main__":
    kindList = get_kind_kwd_list('20200102','20200102','자기주식매매 체결내역')
    CntCheckList=kindList.shape[0]
    totalList=pd.DataFrame()
    if CntCheckList>0:
        for i in range(CntCheckList):
            try:
                df=pd.DataFrame()
                reader=KindDownloader()
                html = reader.get_html(kindList.loc[i, 'rcept_no'])
                tb=get_html_tables(html)
                time.sleep(0.2)
                cnt=len(tb)
                #유가증권과 코스닥 시장 구분 필요, 코넥스 제외 필요
                for t in range(1,cnt):
                    colHead=[col.strip() for col in tb[t].columns]
                    if '유가증권' in kindList.loc[i, 'rcept_no']:
                        tb[t].columns
                    tb[t].columns=colHead
                    tb[t]=tb[t].replace('\n','',regex=True)
                    df=df.append(tb[t])

                df['체결일자']=tb[0].iloc[0,0]
                totalList=totalList.append(df, ignore_index=True)
                del reader

                #time.sleep(1)

            except Exception as e:
                print(e)
                #dartList에서 삭제
                #Load 실패시 다음 조회 루프에서 재조회하기 위함