import streamlit as st

#Python -m streamlit run StreamlitData/HomePage.py  
#streamlit run streamlit_app.py
#st.set_page_config(page_title='Capturando Datos')
#st.title('Oficina Chile & Perú')
#st.sidebar.success('Select a page above.')
#st.subheader("Procesamiento de datos - Cierre Financiero 2025")

# Page Setup
AboutProject=st.Page(
    page='Pages/AboutProject.py',
    title='Home',
    default=True,
    )
Capturing_Oneliner=st.Page(
    page='Pages/Capturing_Oneliner.py',
    title='Oneliner',
    )
Report_DRO=st.Page(page='Pages/Report_DRO.py',
                   title='DRO',
                   )

# Navigation Setup
pg= st.navigation(pages=[AboutProject,Capturing_Oneliner,Report_DRO])

#Run Navigation
pg.run()
