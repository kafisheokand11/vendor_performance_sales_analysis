import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s-%(levelname)s-%(message)s",
    filemode="a"
)

engine=create_engine('sqlite:///inventory.db')

# create a function of ingest_db in which when new data has comes than automaticaly store
def ingest_db(df,table_name,engine):
    df.to_sql(table_name,con=engine,if_exists='replace',index='False')

def load_raw_data():
    # this function will load from csv to data frame and ingest in db
    start=time.time()
    for file in os.listdir('data'): 
        df=pd.read_csv('data/'+file)
        logging.info(f"ingestiing {file} in db")
# call the function ingest_db in which new data will be storing every time. in file name we rempve last 4 char which are '.csv
        ingest_db(df,file[:-4],engine)
    end=time.time()
    total_time=(start-end)/60
    logging.info(f'time taken in ingestion if {total_time} in minutes')
    logging.info("ingesting file complete")