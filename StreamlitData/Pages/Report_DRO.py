import pandas as pd
import sqlalchemy as sa
import pyodbc
from tkinter import filedialog 
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
import streamlit as st
import time


today = date.today()
def fecha_a_usar(fecha):
    FechaAcargar = fecha#'2024-04-01'  
    MesAnterior= FechaAcargar-relativedelta(months=1)
    FechaAcargar=FechaAcargar.replace(day=1)
    MesAnterior=MesAnterior.replace(day=1)
    return  FechaAcargar,MesAnterior




def create_db_engine():
    server = 'Arcappcl002.arcadis.cl'
    database = 'ACLDB'
    username = 'BZIntelligence'
    password = '7EsZ&A~h68'

    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    # Create the database engine for SQL Server
    connection_url = sa.engine.URL.create(
    "mssql+pyodbc", query=dict(odbc_connect=conn_str))
    engine = sa.create_engine(connection_url, fast_executemany=True)
    return engine

Country='ACL'


def main():
    st.title("Procesamiento de Datos DRO")
    engine= create_db_engine()  
    d = st.date_input("Date Period", value=today)
    st.write("Period of the data load:", d.strftime("%Y/%m"))
    FechaAcargar,MesAnterior=fecha_a_usar(d)
    st.subheader("Arcadis Chile")
    archivo_datos=st.file_uploader("Subir Excel",type=['xlsx'])

    if archivo_datos is not None:
        detalles_archivo={"nombre_archvio": archivo_datos.name,"tipo_archivo":archivo_datos.type,"tamaño_archivo":archivo_datos.size}
        if detalles_archivo['tipo_archivo']=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            DF= pd.read_excel(archivo_datos,sheet_name='Facturacion Pendiente',header=2)
            DF_WIP= pd.read_excel(archivo_datos,sheet_name='Antigüedad-IngDevengados',header=5)
            st.subheader('Facturacion Pendiente')
            st.write(DF)
            st.subheader('Antigüedad-IngDevengados')
            st.write(DF_WIP)
            if st.button("Upload to SQL"):
                T1,DF_WIP=CleaningDataDRO_ACL(DF,DF_WIP,FechaAcargar)
                # Create progress bar
                progress_bar = st.progress(0)
                # To SQL
                T1.to_sql("Finance_AccountsReceivable", engine, index=False, if_exists="append", schema="dbo")
                DF_WIP.to_sql("Finance_WIP", engine, index=False, if_exists="append", schema="dbo")
                # End To SQL
                #st.switch_page(page='HomePage.py')
                progress_bar.progress(100)
                st.success("Data successfully uploaded to Sql:")
                time.sleep(1)
                st.switch_page(page='Streamlit_app.py')

def CleaningDataDRO_ACL(DF,DF_WIP,FechaAcargar):
    FechaAcargar2=FechaAcargar.strftime("%Y-%m")
    print(FechaAcargar2)
    DF=DF[['Periodo','Proy.','Descrp','Antigüedad_Elv.','Emisión','Cliente','Total','JP']]
    DF=DF[DF['Periodo']==FechaAcargar2]
    #DF=DF[DF['Periodo']=='2024-05']
    DF['Antigüedad_Elv.']=DF['Antigüedad_Elv.'].astype('category')

    DF_WIP=DF_WIP[['Project','PrjCodeName','Ingresos Devengado','Current','30','60','90','120','>120','Jefe Proyecto']]

    Columns_Rename={'Antigüedad_Elv.':'Antiguedad_Elv','JP':'ProjectManager'}
    Columns_Rename2={'Ingresos Devengado':'Ingresos_Devengado','30':'WIP30','60':'WIP60','90':'WIP90','120':'WIP120','>120':'WIP_More120','Jefe Proyecto':'ProjectManager'}

    DF.rename(columns=Columns_Rename,inplace=True)
    DF_WIP.rename(columns=Columns_Rename2,inplace=True)

    # Working AR 
    T2=DF.drop_duplicates(subset='Proy.',keep='first')
    T2=T2[['Proy.','Descrp','Cliente']]
    T1=DF.groupby(['Proy.', 'Antiguedad_Elv'])['Total'].aggregate('sum').unstack()

    ListadoOriginal=T1.columns.values
    Listado={'1 - 30 días':'Overdue30d','31 - 60 días':'Overdue60d','61 - 90 días':'Overdue90d','mas 365 días':'TotalOverdue'}
    Columns_Rename={}
    for i in Listado:
        if i in ListadoOriginal:
            print(Listado[i])
            Columns_Rename[i]=Listado[i]
        else:
            T1[Listado[i]]=0
    # Columns_Rename={'1 - 30 días':'Overdue30d','mas 365 días':'Overdue90d'}
    T1.rename(columns=Columns_Rename,inplace=True)

    T1['TotalOverdue']=T1['Overdue30d']+T1['Overdue60d']+T1['Overdue90d']+T1['TotalOverdue']
    T1['Overdue30d']=T1['Overdue30d']
    T1['Overdue60d']=T1['Overdue60d']
    T1['Overdue90d']=T1['Overdue90d']
    T1['Overdue_60_90']=T1['Overdue60d']+T1['Overdue90d']

    T1=T1.merge(T2,how='left',on='Proy.')

    T1['TagAR']=T1[['TotalOverdue','Proy.']].apply(lambda x: 'AR' if x['Proy.'][4]=='P' and x['TotalOverdue']> 0 else '',axis=1)
    T1['BIDataPosition']=pd.to_datetime(FechaAcargar)
    # End Work AR

        # Working WIP
    DF_WIP['WIP90']=DF_WIP['WIP90']+DF_WIP['WIP120']+DF_WIP['WIP_More120']
    DF_WIP['TotalWip']=DF_WIP['Current']+DF_WIP['WIP30']+DF_WIP['WIP60']+DF_WIP['WIP90']
    DF_WIP['WIP_60_90']=DF_WIP['WIP60']+DF_WIP['WIP90']
    DF_WIP['ProjectNo']=DF_WIP['Project'].str[0:4].astype(int)
    DF_WIP['TagWIP']= DF_WIP['Ingresos_Devengado'].apply(lambda x: 'WIP' if x > 0  else '')
    DF_WIP=DF_WIP[['Project','ProjectNo','PrjCodeName','Ingresos_Devengado','TotalWip','WIP30','WIP60','WIP90','WIP_60_90','TagWIP']]
    DF_WIP['BIDataPosition']=pd.to_datetime(FechaAcargar)
    DF_WIP['Country']="ACL"
    T1['Country']="ACL"
    return T1,DF_WIP
    # End work WIP

if __name__== '__main__':
    main()

