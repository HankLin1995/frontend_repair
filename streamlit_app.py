import streamlit as st
import pandas as pd

if "user_mail" not in st.session_state:
    st.session_state.user_mail = "test@example.com"

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = 1

if "defect_unique_code" not in st.session_state:
    st.session_state.defect_unique_code = None

VERSION="1.0.1"

st.set_page_config(page_title="缺失追蹤系統" +VERSION, page_icon="🛠️",layout="wide")
st.logo("logo2.png",size="medium")

#get parameters from url

if st.query_params.get("defect_unique_code"):
    st.session_state.defect_unique_code = st.query_params.get("defect_unique_code")
    repair_page=st.Page("view_defect_repair.py", title="修繕", icon=":material/work:")

    pg=st.navigation(
        {
            "修繕": [repair_page]
        }
    )
    pg.run()
else:   
    users_page = st.Page("view_users.py", title="用戶清單", icon=":material/groups:")  # 多個用戶 => groups
    user_page = st.Page("view_user.py", title="用戶詳情", icon=":material/person:")  # 個別用戶 => person
    projects_page = st.Page("view_projects.py", title="工程列表", icon=":material/work:")  # 專案清單 => work
    project_page = st.Page("view_project.py", title="工程詳情", icon=":material/folder_open:")  # 詳情或內容 => folder_open
    # project_partner_page = st.Page("view_project_partner.py", title="工作夥伴", icon=":material/group_work:")  # 協作 => group_work
    defect_page = st.Page("view_defects.py", title="缺失列表", icon=":material/bug_report:")  # 缺失 => bug_report
    defect_add_page = st.Page("view_defect_add.py", title="缺失表單", icon=":material/assignment:")  # 缺失詳情/新增 => assignment
    dashboard_page = st.Page("view_dashboard.py", title="儀錶板", icon=":material/dashboard:")  # 儀錶板 => dashboard（保留原來的）
    # dashboard_new_page = st.Page("view_dashboard_new.py", title="儀錶板", icon=":material/dashboard:")  # 儀錶板 => dashboard（保留原來的）

    pg=st.navigation(
        {
            #"用戶": [users_page,user_page],
            "專案": [projects_page,project_page],
            "缺失": [defect_page,defect_add_page],
            "統計": [dashboard_page]
        }
    )

    pg.run()
