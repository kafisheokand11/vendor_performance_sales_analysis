import sqlite3
import pandas as pd
import logging
from ingestion_db import ingest_db

logging.basicConfig(
    filename="logs/get_vendor_summery.py",
    level=logging.DEBUG,
    format="%(asctime)s-%(levelname)s-%(message)s",
    filemode="a"
)

def create_vendor_summery(conn):
    '''this function will merge the differnt tables in one to get the vendor summery and add new columns in resultant data'''
    vendor_sales_summary = pd.read_sql_query("""WITH FreightSummary AS (SELECT
    VendorNumber,
    SUM(Freight) AS FreightCost
    FROM vendor_invoice
    GROUP BY VendorNumber),
    PurchaseSummary AS (
    SELECT
        p.VendorName,
        p.VendorNumber,
        p.Description,
        p.Brand,
        pp.Volume,
        pp.Price AS ActualPrice,
        p.PurchasePrice,
        SUM(p.Quantity) AS TotalPurchaseQuantity,
        SUM(p.Dollars) AS TotalPurchaseDollars
        FROM purchases p
        JOIN purchase_prices pp
        ON p.Brand = pp.Brand
        WHERE p.PurchasePrice > 0
        GROUP BY
        p.VendorName,
        p.VendorNumber,
        p.Brand,
        p.Description,
        p.PurchasePrice,
        pp.Price,
        pp.Volume),
        
        SalesSummary AS (SELECT
        VendorNo,
        Brand,
        SUM(SalesDollars) AS TotalSalesDollars,
        SUM(SalesPrice) AS TotalSalesPrice,
        SUM(SalesQuantity) AS TotalSalesQuantity,
        SUM(ExciseTax) AS TotalTax
        FROM sales GROUP BY VendorNo, Brand
        )
        
        SELECT 
        ps.VendorNumber,
        ps.VendorName,
        ps.Brand,
        ps.Description,
        ps.PurchasePrice,
        ps.ActualPrice,
        ps.Volume,
        ps.TotalPurchaseQuantity,
        ps.TotalPurchaseDollars,
        ss.TotalSalesDollars,
        ss.TotalSalesQuantity,
        ss.TotalSalesPrice,
        ss.TotalTax,
        fs.FreightCost
        FROM PurchaseSummary ps
        LEFT JOIN SalesSummary ss
        ON ps.VendorNumber = ss.VendorNo AND ps.Brand = ss.Brand
        LEFT JOIN FreightSummary fs
        ON ps.VendorNumber = fs.VendorNumber
        ORDER BY ps.TotalPurchaseDollars DESC;""", conn)
        return vendor_sales_summery

def clean_Data(df):
    #changing the data type of column
    df['Volume']=df["Volume"].astype('float')

    #to fill the null value
    df.fillna(0,inplace=True)

    # to remove the extra space 
    df['VendorName'].str.strip()
    df['Description'].str.strip()

    # add new column
    df['Gross_profit']=df['TotalSalesDollars']-df['TotalPurchaseDollars']
    df['Profit_margin']=(df['Gross_profit']/df['TotalSalesDollars'])*100
    df['StockTurnOver']=df['TotalPurchaseQuantity']/df['TotalSalesQuantity']
 return df

if __name__=='__main__':
    conn=sqlite3.connect('inventory.db')

    logging.info('creating vendor summery table')
    summery_df=create_vendor_summery(conn)
    logging.info(summery_df.head())

    logging.info('cleaning the data')
    clean_df=clean_data(summery_df)
    logging.info(clean_df.head())

    logging.info('create an ingesting data')
    ingest_db(clean_df,'vendor_sales_summary',conn)
    logging.info('completed')


        



