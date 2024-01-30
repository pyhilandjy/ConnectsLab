from sqlalchemy import create_engine
import pandas as pd

def to_db(table, df):
    """적재할 table, 변수"""
    db_user = 'root'
    db_password = '1234qwer'
    db_host = 'mysql'
    db_port = 3306  # MySQL 포트
    db_name = 'STT'

    # MySQL 연결 엔진 생성
    engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    df.to_sql(table, con=engine, if_exists='replace', index=False)