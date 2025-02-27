import streamlit as st

#Python -m streamlit run StreamlitData/HomePage.py  https://github.com/shokiche92/ProcesamientoDeDatos/blob/main/StreamlitData/HomePage.py

st.set_page_config(page_title='Multipage App')
st.title('Oficina Chile & Perú')

st.subheader("Procesamiento de datos - Cierre Financiero 2025")
options=st.sidebar.radio('Select:',['HomePage','Capturing_Oneliner','Report_DRO'])

def HomePage():
    st.switch_page(page='HomePage.py')
def Capturing_Oneliner():
    st.switch_page(page='Capturing_Oneliner.py')
def Report_DRO():
    st.switch_page(page='Report_DRO.py')

#Navigation Option
if options== 'HomePage':
    HomePage()
elif options=='Capturing_Oneliner':
    Capturing_Oneliner()
elif options=='Report_DRO' :
    Report_DRO()
    

