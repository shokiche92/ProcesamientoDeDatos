import streamlit as st

#Python -m streamlit run StreamlitData/HomePage.py  
#streamlit run StreamlitData/streamlit_app.py


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

# Navigation Setup Without sections
#pg= st.navigationpages=[project_1_page,project_2_page,project_3_page])

# Navigations setup With section
pg=st.navigation(
    {
        'Inicial':[project_1_page],
        'Proyectos':[project_2_page,project_3_page],
    }
)

#Run Navigation
pg.run()