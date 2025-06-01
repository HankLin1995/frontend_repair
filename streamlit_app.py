import streamlit as st
import pandas as pd

if "user_id" not in st.session_state:
    st.session_state.user_id = "test@example.com"

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = 1

st.set_page_config(page_title="工程缺失管理系統", page_icon=":material/edit_document:",layout="wide")
st.logo("logo.jpg")

users_page=st.Page("view_users.py", title="用戶清單", icon=":material/star:")
vendor_page=st.Page("view_vendors.py", title="廠商清單", icon=":material/storefront:")
category_page=st.Page("view_categories.py", title="分類清單", icon=":material/storefront:")
projects_page = st.Page("view_projects.py", title="工程列表", icon=":material/view_list:")
project_page = st.Page("view_project.py", title="工程詳情", icon=":material/description:")
project_partner_page = st.Page("view_project_partner.py", title="工作夥伴", icon=":material/description:")
defect_page = st.Page("view_defects.py", title="缺失清單", icon=":material/list:")
defect_add_page = st.Page("view_defect_add.py", title="新增缺失", icon=":material/circle:")

pg=st.navigation(
    {
        "基本設定": [vendor_page,users_page,category_page],
        "工程管理": [projects_page,project_partner_page],
        "缺失管理": [defect_page,defect_add_page]
    }
)

pg.run()