import os
from dotenv import load_dotenv

load_dotenv()
# .env 저장
host = os.getenv('DB_HOST', '')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER', '')
password = os.getenv('DB_PASSWORD', '')
database = os.getenv('DB_NAME', 'stock_db')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

def load_stock_infos():
    with engine.connect() as conn:
        query = "SELECT * FROM tb_stock"
        return pd.read_sql(query, conn)

def load_data(stock_id):
    with engine.connect() as conn:
        query = "SELECT * FROM tb_price WHERE stock_id=%s ORDER BY created_at DESC LIMIT 100"
        return pd.read_sql(query, conn, params=(stock_id, ))