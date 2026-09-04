import time
import random
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData
from datetime import datetime

# SQLite 데이터베이스 연결
engine = create_engine('sqlite:///stocks.db')
metadata = MetaData()

# 테이블 정의
stocks_table = Table('stocks', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('timestamp', String),
                     Column('price', Float),
                     Column('volume', Integer))

# 테이블 생성
metadata.create_all(engine)

def add_fake_stock_data():
    with engine.connect() as conn:
        # 가상의 주식 데이터 생성
        price = random.uniform(100, 200)  # 주식 가격
        volume = random.randint(1000, 5000)  # 거래량
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 데이터 삽입
        conn.execute(stocks_table.insert().values(
            timestamp=timestamp,
            price=price,
            volume=volume
        ))
        conn.commit()

if __name__ == "__main__":
    while True:
        add_fake_stock_data()
        print("Added new stock data.")
        time.sleep(0.2)