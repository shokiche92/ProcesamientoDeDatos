import streamlit as st
import pandas as  pd
import numpy as np
from datetime import date, timedelta,datetime
#from st_on_hover_tabs import on_hover_tabs
from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
import time
# python -m streamlit run CapturingData.py   

today = date.today()


#st.set_page_config(page_title="Capturing Data Oneliner",layout="wide")

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

def CleaningDataACL(df,FechaAcargar,eleccion):

    Headline=['PY','Status Planner','GR MTD','NR MTD','CD MTD','GM MTD','GM% MTD','Mult MTD','EBITA Real  MTD','Oper EBITA Mult','Oper. EBITA% Mult MTD','LMP MTD','GR YTD','NR YTD','CD YTD','GM YTD','GM% YTD','Mult YTD','EBITA REAL YTD','EBITA YTD Mult','EBITA% YTD Mult','LMP YTD','GR PTD','NR PTD','CD PTD','GM PTD','GM% PTD','Mult PTD','EBITA PTD','EBITA% PTD','LMP PTD','GR EAT','NR EAT','CD EAT','GM EAT','GM% EAT','Mult EAT','EBITA EAT','EBITA% EAT','LMP EAT','GR Backlog','NR Backlog','CD Backlog','GM Backlog','GM% Backlog','Mult Backlog','EBITA Backlog','EBITA% Backlog','LMP Backlog','GR PR0','NR PR0','CD PR0','GM PR0','GM% PR0','Mult PR0','EBITA PR0','EBITA% PR0','LMP PR0','Breakeven Mult','GR 3 últimos meses','Ingreso Devengado','Cuentas por Cobrar','Retenciones','Relacionadas','AR Open','Project - Aging Buckets Current','Project - Aging Buckets 1-30 Days','Project - Aging Buckets 31-60 Days','Project - Aging Buckets 61-90 Days','Project - Aging Buckets 91-180 Days','Project - Aging Buckets 181-360 Days','Project - Aging Buckets 361+ Days','Total Revenue Outstanding','DUO','DBO','DRO','DRO_Cia','BEM Real YTD','EBITA REAL MTD','EBITA REAL YTD2','NET OI OFICIAL','Performance YTD','Det Performance YTD','Category YTD','Performance PTD','Det Performance PTD','Category PTD','Nombre Proyecto','AW Category','Inicio','Termino','Breakeven Mult PR0']
    Columns_Rename={'GM%_MTD':'Percent_GM_MTD','Oper_EBITA%_Mult_MTD':'Percent_Oper_EBITA_Mult_MTD','GM%_YTD':'Percent_GM_YTD','EBITA%_YTD_Mult':'Percent_EBITA_YTD_Mult','GM%_PTD':'Percent_GM_PTD','EBITA%_PTD':'Percent_EBITA_PTD','GM%_EAT':'Percent_GM_EAT','EBITA%_EAT':'Percent_EBITA_EAT','GM%_Backlog':'Percent_GM_Backlog','EBITA%_Backlog':'Percent_EBITA_Backlog','GM%_PR0':'Percent_GM_PR0','EBITA%_PR0':'Percent_EBITA_PR0'}
    df= df[Headline]
    df['ProjectNo']=df['PY'].str[0:4].astype(int)
    df['BIDataPosition']=pd.to_datetime(FechaAcargar).strftime("%Y-%m-01")
    df['Country']=str(eleccion)
    df.columns = [str(col).replace(' ','_') for col in df.columns]
    df.columns = [str(col).replace('-','') for col in df.columns]
    df.columns = [str(col).replace('.','') for col in df.columns]
    df.columns = [str(col).replace('+','More') for col in df.columns]
    filas=len(df)
    df.rename(columns=Columns_Rename,inplace=True)
    df['Nombre_Proyecto']=df['Nombre_Proyecto'].str.strip()
    
    df=df.fillna(0)
    df = df.query('BIDataPosition=="'+pd.to_datetime(FechaAcargar).strftime("%Y-%m-01")+'"' )
    df_LMP=df[df['EBITA_YTD_Mult']<0]
    df_LMP=df_LMP[['PY','EBITA_YTD_Mult']].sort_values(by=['EBITA_YTD_Mult'])
    df_LMP=df_LMP.iloc[:10,:]
    df_LMP=df_LMP[['PY']]
    df_LMP['Tag_LMP_Z']='LMP'
    
    df_Under=df.loc[(df['Mult_YTD']>df['Breakeven_Mult']) & (df['Mult_PR0'] > df['Mult_YTD'])]
    df_Under=df_Under[['PY','EBITA_YTD_Mult']].sort_values(by=['EBITA_YTD_Mult'])
    df_Under=df_Under[['PY']]
    df_Under['Tag_LMP_Y']='Underperforming'
    df= df.merge(df_LMP,on='PY',how='left')
    df= df.merge(df_Under,on='PY',how='left')
    df['Tag_LMP']=df[['Tag_LMP_Z','Tag_LMP_Y']].apply(lambda x: "LMP" if x['Tag_LMP_Z']=='LMP' else x['Tag_LMP_Y'],axis=1)
    df=df.drop(['Tag_LMP_Z','Tag_LMP_Y'],axis=1)
    df['Year_BIDataPosition']= pd.to_datetime(FechaAcargar).year
    df['Month_BIDataPosition']=pd.to_datetime(FechaAcargar).month
    #st.dataframe(df)
    return df

def CleaningDataAPE(df,FechaAcargar,eleccion):   
    Headline=['PY','Status Planner','GR MTD','NR MTD','CD MTD','GM MTD','GM% MTD','Mult MTD','EBITA Real  MTD','Oper EBITA Mult','Oper. EBITA% Mult MTD','LMP MTD','GR YTD','NR YTD','CD YTD','GM YTD','GM% YTD','Mult YTD','EBITA REAL YTD','EBITA YTD Mult','EBITA% YTD Mult','LMP YTD','GR PTD','NR PTD','CD PTD','GM PTD','GM% PTD','Mult PTD','EBITA PTD','EBITA% PTD','LMP PTD','GR EAT','NR EAT','CD EAT','GM EAT','GM% EAT','Mult EAT','EBITA EAT','EBITA% EAT','LMP EAT','GR Backlog','NR Backlog','CD Backlog','GM Backlog','GM% Backlog','Mult Backlog','EBITA Backlog','EBITA% Backlog','LMP Backlog','GR PR0','NR PR0','CD PR0','GM PR0','GM% PR0','Mult PR0','EBITA PR0','EBITA% PR0','LMP PR0','Breakeven Mult','GR 3 últimos meses','Ingreso Devengado','Cuentas por Cobrar','Retenciones','Relacionadas','AR Open','Project - Aging Buckets Current','Project - Aging Buckets 1-30 Days','Project - Aging Buckets 31-60 Days','Project - Aging Buckets 61-90 Days','Project - Aging Buckets 91-180 Days','Project - Aging Buckets 181-360 Days','Project - Aging Buckets 361+ Days','Total Revenue Outstanding','DUO','DBO','DRO','DRO_Cia','BEM Real YTD','EBITA REAL YTD2','NET OI OFICIAL','Performance YTD','Det Performance YTD','Category YTD','Performance PTD','Det Performance PTD','Category PTD','Nombre Proyecto','AW Category','Inicio','Termino','Breakeven Mult PR0']
    Columns_Rename={'GM%_MTD':'Percent_GM_MTD','Oper_EBITA%_Mult_MTD':'Percent_Oper_EBITA_Mult_MTD','GM%_YTD':'Percent_GM_YTD','EBITA%_YTD_Mult':'Percent_EBITA_YTD_Mult','GM%_PTD':'Percent_GM_PTD','EBITA%_PTD':'Percent_EBITA_PTD','GM%_EAT':'Percent_GM_EAT','EBITA%_EAT':'Percent_EBITA_EAT','GM%_Backlog':'Percent_GM_Backlog','EBITA%_Backlog':'Percent_EBITA_Backlog','GM%_PR0':'Percent_GM_PR0','EBITA%_PR0':'Percent_EBITA_PR0'}
    df= df[Headline]
    df.columns = [str(col).replace(' ','_') for col in df.columns]
    df.columns = [str(col).replace('-','') for col in df.columns]
    df.columns = [str(col).replace('.','') for col in df.columns]
    df.columns = [str(col).replace('+','More') for col in df.columns]
    filas=len(df)
    df.rename(columns=Columns_Rename,inplace=True)
   
    df['Nombre_Proyecto']=df['Nombre_Proyecto'].str.strip()
    df['BIDataPosition']=pd.to_datetime(FechaAcargar).strftime("%Y-%m-01")
    df['Country']=str(eleccion)
    df=df.fillna(0)
    Headers= list(df.columns.values)
    # extraer los comentarios anteriores
    df['EBITA_YTD_Mult']=df['EBITA_REAL_YTD']
    df['Performance_YTD']=df['NR_YTD']-(df['CD_YTD']*df['Mult_PR0'])

    df['Performance_YTD']=df.apply(lambda x : x.EBITA_YTD_Mult if x.Mult_PR0 < 0 else x.Performance_YTD,axis=1)

    df = df.query('BIDataPosition=="'+pd.to_datetime(FechaAcargar).strftime("%Y-%m-01") +'"' )
    df_LMP=df[(df['EBITA_YTD_Mult']<0) & (df['Status_Planner']!='Cerrado')]
    df_LMP=df_LMP[['PY','EBITA_YTD_Mult']].sort_values(by=['EBITA_YTD_Mult'])
    df_LMP=df_LMP.iloc[:10,:] #Choose the top ten
    df_LMP=df_LMP[['PY']]
    df_LMP['Tag_LMP_Z']='LMP'
    
    df_Under=df.loc[(df['Mult_YTD']>df['Breakeven_Mult']) & (df['Mult_PR0'] > df['Mult_YTD'])& (df['Status_Planner']!='Cerrado')]
    df_Under=df_Under[['PY','EBITA_YTD_Mult']].sort_values(by=['EBITA_YTD_Mult'])
    df_Under=df_Under[['PY']]
    df_Under['Tag_LMP_Y']='Underperforming'

    df= df.merge(df_LMP,on='PY',how='left')
    df= df.merge(df_Under,on='PY',how='left')
    
    df['Tag_LMP']=df[['Tag_LMP_Z','Tag_LMP_Y']].apply(lambda x: "LMP" if x['Tag_LMP_Z']=='LMP' else x['Tag_LMP_Y'],axis=1)
    

    df=df.drop(['Tag_LMP_Z','Tag_LMP_Y'],axis=1)
    df['Year_BIDataPosition']= pd.to_datetime(FechaAcargar).year
    df['Month_BIDataPosition']=pd.to_datetime(FechaAcargar).month
    df['ProjectNo']=df['PY'].astype(int)
    return df
 
def main():
    st.title("Proceso de carga de datos")
    menu=["ACL","APE"]
    eleccion=st.sidebar.selectbox("Menú",menu)
    engine= create_db_engine()  
    d = st.date_input("Date Period", value=today)
    st.write("Period of the data load:", d.strftime("%Y/%m"))
    FechaAcargar,MesAnterior=fecha_a_usar(d)
    if eleccion =="ACL":
        st.subheader("Arcadis Chile")
        archivo_datos=st.file_uploader("Subir Excel",type=['xlsx'])
        if archivo_datos is not None:
            detalles_archivo={"nombre_archvio": archivo_datos.name,"tipo_archivo":archivo_datos.type,"tamaño_archivo":archivo_datos.size}
            #st.write(detalles_archivo)
            
            if detalles_archivo['tipo_archivo']=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df=pd.read_excel(archivo_datos,sheet_name='Oneliner',header=7)
                df = df.dropna(subset='PY')
                st.write(df)

                if st.button("Upload to SQL"):
                    df=CleaningDataACL(df,FechaAcargar,eleccion)
                
                    # Create progress bar
                    progress_bar = st.progress(0)
                    df.to_sql("FinanceOneliner", engine, index=False, if_exists="append", schema="dbo")
                    #st.switch_page(page='HomePage.py')
                    progress_bar.progress(100)
                    st.success("Data successfully uploaded to Sql:")
                    time.sleep(2)
                    st.switch_page(page='Streamlit_app.py')

    if eleccion =="APE":
        st.subheader("Arcadis Perú")
        archivo_datos=st.file_uploader("Subir Excel",type=['xlsx'])
        if archivo_datos is not None:
            detalles_archivo={"nombre_archvio": archivo_datos.name,"tipo_archivo":archivo_datos.type,"tamaño_archivo":archivo_datos.size}
            st.write(detalles_archivo)
            
            if detalles_archivo['tipo_archivo']=='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                df=pd.read_excel(archivo_datos,sheet_name='Oneliner',header=7)
                df = df.dropna(subset='PY')
                st.button("Upload to SQL")  
                df=CleaningDataAPE(df,FechaAcargar,eleccion)
                
                # Create progress bar
                progress_bar = st.progress(0)
                df.to_sql("FinanceOneliner", engine, index=False, if_exists="append", schema="dbo")
                #st.switch_page(page='HomePage.py')
                progress_bar.progress(100)
                st.success("Data successfully uploaded to Sql:")
                time.sleep(2)
                st.switch_page(page='Streamlit_app.py')

            else:
                df=pd.DataFrame()



if __name__== '__main__':
    main()


