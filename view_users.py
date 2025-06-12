import streamlit as st
import api
import pandas as pd

@st.dialog("新增用戶")
def create_user_ui():
    with st.form("create_user_form"):
        user_name = st.text_input("用戶名稱")
        user_email = st.text_input("電子郵件")
        user_role = st.selectbox("角色", ["擁有者", "協作者", "檢視者"])
        phone = st.text_input("電話")
        line_id = st.text_input("Line ID")
        submit_button = st.form_submit_button("新增用戶")
        if submit_button:
            if not user_name or not user_email:
                st.warning("請輸入用戶名稱與電子郵件")
                return
            try:
                result = api.create_user(user_name, user_email, user_role, phone, line_id)
                if result:
                    st.success(f"用戶 '{user_name}' 已新增")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"新增用戶時發生錯誤: {str(e)}")

@st.dialog("編輯用戶")
def edit_user_ui(user):
    # st.write(user)
    # with st.form("edit_user_form"):
    user_name = st.text_input("用戶名稱", value=user['name'])
    user_email = st.text_input("電子郵件", value=user['email'],disabled=True)
    company_name=st.text_input("公司名稱", value=user.get('company_name', ''))
    # user_role = st.selectbox("角色", ["擁有者", "協作者", "檢視者"], index=["擁有者", "協作者", "檢視者"].index(user['role']) if user['role'] in ["擁有者", "協作者", "檢視者"] else 1)
    phone = st.text_input("電話", value=user.get('phone', ''))
    line_id = st.text_input("Line ID", value=user.get('line_id', ''))
    
    submit_button = st.button("更新用戶")
    if submit_button:
        if not user_name or not user_email:
            st.warning("請輸入用戶名稱與電子郵件")
            return
        try:
            result = api.update_user(user['user_id'], user_name, user_email, company_name, phone, line_id)
            if result:
                st.success(f"用戶 '{user_name}' 已更新")
                st.rerun()
            else:
                st.error("API 返回失敗結果")
        except Exception as e:
            st.error(f"更新用戶時發生錯誤: {str(e)}")

users = api.get_users()

df = pd.DataFrame(users)

if df.empty:
    st.info("目前尚無用戶資料，請新增用戶。")
    st.stop()

#加入 http://localhost:8000
df['avatar_path'] = df['avatar_path'].apply(lambda x: "http://localhost:8000/"+x if x else "")

if not df.empty:
    event = st.dataframe(
        df,
        column_config={
            "name": "姓名",
            "avatar_path": None,#st.column_config.ImageColumn(),
            "email": "電子郵件",
            "company_name": "公司名稱",
            "phone": "電話",
            "line_id": "Line ID",
            "user_id":None,
            "created_at": "建立時間",
        },
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
        use_container_width=True
    )
    if event.selection.rows:
        selected_row = event.selection.rows[0]
        selected_user = df.iloc[selected_row]
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 編輯", key=f"edit_{selected_user['user_id']}", use_container_width=True):
                edit_user_ui(selected_user)
                # st.rerun()
        with col2:
            if st.button("🗑️ 刪除", key=f"delete_{selected_user['user_id']}", use_container_width=True):
                api.delete_user(selected_user['user_id'])
                st.rerun()
else:
    st.info("目前尚無用戶資料，請新增用戶。")

st.markdown("---")
if st.button("新增用戶"):
    create_user_ui()
