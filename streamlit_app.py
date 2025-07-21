import streamlit as st
import pandas as pd

if "user_mail" not in st.session_state:
    st.session_state.user_mail = "user@example.com"

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = 1

if "defect_unique_code" not in st.session_state:
    st.session_state.defect_unique_code = None

def login_info():
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 使用說明")
        st.markdown("""
        1. **登入 Google 帳號**  
        2. **建立工程**  
        3. **新增抽查表**  
            - 上傳 PDF  
            - 填寫基本資料  
            - 上傳多張照片  
        4. **查看清單並列印報告**
                """)

    with col2:
        st.markdown("### ⚠️ 注意事項")
        st.warning("""
        - 系統目前部署在我的個人主機  
        - 如需部署在指定主機，歡迎聯繫我！
                """)

        st.divider()

        st.markdown("### 📬 聯絡資訊")

        col3,col4 = st.columns(2)

        with col3:
            st.image("https://www.hanksvba.com/images/LINE_QRCODE.PNG", width=150, caption="LINE官方帳號")

        with col4:

            st.link_button("🌎 Hank's blog", "https://www.hanksvba.com/",type="secondary")

def main():

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

###########################

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

    if not st.user.is_logged_in:
        login_info()
        if st.sidebar.button("Google 登入",type="primary"):
            st.login()
    else:
        main()
        if st.sidebar.button(f"👋 {st.user.name}登出",type="secondary"):
            st.logout()

    # main()
