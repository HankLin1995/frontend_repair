import streamlit as st
import pandas as pd

project_page= st.Page("view_projects.py", title="專案管理", icon=":material/edit_document:")

pg=st.navigation(
    {
        "設定": [project_page]
    }
)

pg.run()