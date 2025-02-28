import streamlit as st

#Python -m streamlit run StreamlitData/HomePage.py  
#streamlit run StreamlitData/streamlit_app.py
#st.set_page_config(page_title='Capturando Datos',layout='wide')
#st.title('Oficina Chile & Perú')
#st.sidebar.success('Select a page above.')
#st.subheader("Procesamiento de datos - Cierre Financiero 2025")

# Page Setup
project_1_page=st.Page(
    page='Pages/AboutProject.py',
    title='Home',
    default=True,
    )
project_2_page=st.Page(
    page='Pages/Capturing_Oneliner.py',
    title='Oneliner',
    )
project_3_page=st.Page(page='Pages/Report_DRO.py',
                   title='DRO',
                   )

# Navigation Setup
pg= st.navigation(pages=[project_1_page,project_2_page,project_3_page])

#Run Navigation
pg.run()
