import streamlit as st
import pandas as pd

if "user_id" not in st.session_state:
    st.session_state.user_id = "test@example.com"

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = 1

st.set_page_config(page_title="工程缺失管理系統", page_icon=":material/edit_document:",layout="wide")
st.logo("logo.jpg")

users_page = st.Page("view_users.py", title="用戶清單", icon=":material/groups:")  # 多個用戶 => groups
user_page = st.Page("view_user.py", title="用戶詳情", icon=":material/person:")  # 個別用戶 => person
projects_page = st.Page("view_projects.py", title="工程列表", icon=":material/work:")  # 專案清單 => work
project_page = st.Page("view_project.py", title="工程詳情", icon=":material/folder_open:")  # 詳情或內容 => folder_open
project_partner_page = st.Page("view_project_partner.py", title="工作夥伴", icon=":material/group_work:")  # 協作 => group_work
defect_page = st.Page("view_defects.py", title="缺失清單", icon=":material/bug_report:")  # 缺失 => bug_report
defect_add_page = st.Page("view_defect_add.py", title="缺失詳情", icon=":material/assignment:")  # 缺失詳情/新增 => assignment
dashboard_page = st.Page("view_dashboard.py", title="儀錶板", icon=":material/dashboard:")  # 儀錶板 => dashboard（保留原來的）


# vendor_page=st.Page("view_vendors.py", title="廠商清單", icon=":material/storefront:")
# category_page=st.Page("view_categories.py", title="分類清單", icon=":material/storefront:")

# pg=st.navigation(
#     {
#         "基本設定": [vendor_page,users_page,category_page],
#         "專案管理": [projects_page,project_partner_page],
#         "缺失管理": [defect_page,defect_add_page]
#     }
# )

pg=st.navigation(
    {
        "用戶": [users_page,user_page],
        "專案": [projects_page,project_page],
        "缺失": [defect_page,defect_add_page],
        "統計": [dashboard_page]
    }
)

pg.run()