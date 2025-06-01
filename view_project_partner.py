import streamlit as st
import api

@st.dialog("新增工作夥伴")
def invite_user():

    user_email = st.text_input("Email")
    user_role = st.selectbox("角色", ["擁有者", "協作者","檢視者"],index=1)
    submit_button = st.button("新增")
    
    if submit_button:
        result = api.create_permission(st.session_state.active_project_id, user_email, user_role)
        if result:
            st.success("工作夥伴新增成功")
            st.rerun()
        else:
            st.error("工作夥伴新增失敗")

@st.dialog("更新權限")
def edit_permission(user):
    
    with st.form("edit_permission_form"):
        new_role = st.selectbox("角色", ["擁有者", "協作者","檢視者"],index=1)
        submit_button = st.form_submit_button("更新")
        
        if submit_button:
            try:
                result = api.update_permission(user['permission_id'], new_role)
                if result:
                    st.success(f"權限 '{new_role}' 已更新")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"更新權限時發生錯誤: {str(e)}")

def display_user_card(users):
    """以卡片形式顯示專案列表"""
    # st.write(users)
    # 顯示專案卡片

    if not users:
        st.info("目前沒有工作夥伴，請新增工作夥伴。")
        return

    cols = st.columns(3)  # 每行4個卡片
    
    for i, user in enumerate(users):
        with cols[i % 3]:
            with st.container(border=True):
                col1,col2=st.columns([1,2])
                with col1:
                    # avatar_url = f"https://i.pravatar.cc/150?u={user['user_email']}"
                    if user['avatar_path']!="static/avatar/default.png":
                        avatar_url=f"http://localhost:8000/{user['avatar_path']}"
                    else:
                        avatar_url=f"https://i.pravatar.cc/150?u={user['user_email']}"
                    st.markdown(
                        f"<img src='{avatar_url}' style='border-radius:50%;width:100px;height:100px;object-fit:cover;'>",
                        unsafe_allow_html=True
                    )

                with col2:
                    # st.markdown("**權限ID:** "+ str(user['permission_id']))
                    st.markdown("**電子郵件:** "+ user['user_email'])
                    st.markdown("**姓名:** "+ user['user_name'])
                    st.markdown("**角色:** "+ user['user_role'])
                # st.markdown("---")

                col3,col4=st.columns([1,1])
                with col3:
                    if st.button("編輯",key=f"edit_{user['permission_id']}",use_container_width=True):
                        edit_permission(user)

                with col4:
                    if st.button("刪除",key=f"delete_{user['permission_id']}",use_container_width=True):   
                        api.delete_permission(user['permission_id'])
                        st.rerun()



def display_project_members():

    # with st.container(border=True):

    # st.subheader("👥 工作夥伴")

    roles = api.get_permissions(st.session_state.active_project_id)
    # roles=roles_data['permissions']

    display_user_card(roles)

    st.markdown("---")

    if st.button("新增工作夥伴",type="primary"):
        invite_user()

    if st.session_state.active_project_id is None:
        st.warning("請先至工程列表選擇當前工程!")
        st.stop()

project = api.get_project(st.session_state.active_project_id)

if project:
    st.markdown("#### 工程 / "+project['project_name']+" / 工作夥伴") 

    st.markdown("---")
else:
    st.warning("請先至工程列表選擇當前工程!")
    st.stop()

display_project_members()


