import streamlit as st
import api
from streamlit_extras.floating_button import floating_button
from streamlit_avatar import avatar

@st.dialog("新增底圖")
def create_basemap():
    project_id = st.session_state.active_project_id
    map_name=st.text_input("底圖名稱")
    map_file=st.file_uploader("上傳底圖", type=["png", "jpg", "jpeg"])
    bytes_file=map_file.read()

    submit_button=st.button("新增")
    
    if submit_button:
        result = api.create_basemap(project_id, map_name)
        st.write(result)
        if result:
            st.success("底圖新增成功")
            #建立圖片時發生錯誤: a bytes-like object is required, not 'dict'
            if map_file:
                files = {"file": (map_file.name, bytes_file, map_file.type)}
                try:
                    result2 = api.create_basemap_image(result['base_map_id'], files)
                    if result2:
                        st.success("底圖圖片新增成功")
                    else:
                        st.error("底圖圖片新增失敗")
                except Exception as e:
                    st.error(f"建立圖片時發生錯誤: {str(e)}")
        else:
            st.error("底圖新增失敗")

        st.rerun()


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
                    avatar_url = f"https://i.pravatar.cc/150?u={user['user_email']}"
                    avatar(
                            [
                                {
                                    "url": avatar_url,
                                    "size": 100,
                                    "key": "avatar1",
                                }
                            ]
                        )

                with col2:
                    # st.markdown("**權限ID:** "+ str(user['permission_id']))
                    st.markdown("**電子郵件:** "+ user['user_email'])

                    if user['user_name']:
                        st.markdown("**姓名:** "+ user['user_name'])
                    else:
                        st.warning("該用戶尚未登入過系統",icon="⚠️")

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



def display_project_basemaps():
    basemaps = api.get_basemaps(st.session_state.active_project_id)
    # st.write(basemaps)

    if not basemaps:
        st.info("目前沒有工程底圖，請新增工程底圖。")
        return
    else:
        cols = st.columns(3)  # 每行4個卡片
        
        for i, basemap in enumerate(basemaps):
            with cols[i % 3]:
                with st.container(border=True):
                    st.image("http://localhost:8000/"+basemap['file_path'])
                    st.caption("#### " + basemap['map_name'])
        
    if floating_button(":material/add: 新增工程底圖",key="add_basemap"):
        create_basemap()
    
def display_project_defects():
    pass

def display_project_members():

    # with st.container(border=True):

    # st.subheader("👥 工作夥伴")

    roles = api.get_permissions(st.session_state.active_project_id)
    # roles=roles_data['permissions']

    display_user_card(roles)

    st.markdown("---")

    if floating_button(":material/add: 新增工作夥伴",key="add_partner"):
        invite_user()

    if st.session_state.active_project_id is None:
        st.warning("請先至工程列表選擇當前工程!")
        st.stop()

project = api.get_project(st.session_state.active_project_id)

if project:
    st.caption("工程/ "+project['project_name']) 
else:
    st.warning("請先至工程列表選擇當前工程!")
    st.stop()

tabs=st.tabs(["👥工作夥伴","🗺️工程底圖"])

with tabs[0]:
    display_project_members()
with tabs[1]:
    display_project_basemaps()

