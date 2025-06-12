import streamlit as st
import api
from streamlit_extras.floating_button import floating_button
from streamlit_avatar import avatar
from PIL import Image

def crop_and_resize_image(img, target_w=5760, target_h=3840):
    """
    將圖片裁切為特定比例，並 resize 成指定大小
    """
    target_ratio = target_w / target_h
    w, h = img.size
    img_ratio = w / h

    if img_ratio > target_ratio:
        # 原圖較寬，以高度為準裁切寬度
        crop_h = h
        crop_w = int(h * target_ratio)
    else:
        # 原圖較高或等寬高比，以寬度為準裁切高度
        crop_w = w
        crop_h = int(w / target_ratio)

    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    right = left + crop_w
    bottom = top + crop_h

    cropped_img = img.crop((left, top, right, bottom))
    resized_img = cropped_img.resize((target_w, target_h), Image.LANCZOS)
    return resized_img


def resize_image_keep_ratio(img, max_width=1000):
    w, h = img.size
    if w > max_width:
        ratio = max_width / w
        new_w = max_width
        new_h = int(h * ratio)
        return img.resize((new_w, new_h), Image.LANCZOS)
    return img

@st.dialog("新增底圖")
def create_basemap():
    project_id = st.session_state.active_project_id
    map_name=st.text_input("底圖名稱")
    map_file=st.file_uploader("上傳底圖", type=["png", "jpg", "jpeg"])
    if map_file:
        import io
        img = Image.open(map_file)
        preview_img = resize_image_keep_ratio(img, 1200)
        st.image(preview_img)
        # map_file_new = crop_and_resize_image(img, 1000, 562)
        buf = io.BytesIO()
        preview_img.save(buf, format="JPEG")
        bytes_file = buf.getvalue()

        submit_button=st.button("新增",use_container_width=True)

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
    submit_button = st.button("新增",use_container_width=True)
    
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
                        st.warning("尚未登入過系統",icon="⚠️")

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

@st.dialog("編輯工程底圖")
def edit_basemap(basemap):
    with st.form("edit_basemap_form"):
        map_name=st.text_input("底圖名稱",value=basemap['map_name'])
        submit_button=st.form_submit_button("更新")
        if submit_button:
            result = api.update_basemap(basemap['base_map_id'], map_name)
            if result:
                st.success("底圖已更新")
                st.rerun()
            else:
                st.error("底圖更新失敗")

def display_project_basemaps():
    basemaps = api.get_basemaps(st.session_state.active_project_id)
    # st.write(basemaps)

    if not basemaps:
        st.info("目前沒有工程底圖，請新增工程底圖。")
        # return
    else:
        cols = st.columns(3)  # 每行4個卡片
        
        for i, basemap in enumerate(basemaps):
            with cols[i % 3]:
                with st.container(border=True):
                    st.image("http://localhost:8000/"+basemap['file_path'])
                    st.markdown("#### " + basemap['map_name'])
                    col3,col4=st.columns([1,1])
                    with col3:
                        if st.button("刪除",key=f"delete_{basemap['base_map_id']}_i",use_container_width=True):   
                            api.delete_basemap(basemap['base_map_id'])
                            st.rerun()
                    with col4:
                        if st.button("編輯",key=f"edit_{basemap['base_map_id']}_i",use_container_width=True):
                            edit_basemap(basemap)
        
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

tabs = st.tabs([
    "👥 夥伴",      # or keep 👥
    "🗺️ 底圖",      # current one is good
    "🏷️ 分類",      # new emoji for categories
    "🏭 廠商"       # new emoji for vendors
])

with tabs[0]:
    display_project_members()
with tabs[1]:
    display_project_basemaps()
with tabs[2]:
    # display_project_defects()
    pass
with tabs[3]:
    # display_project_defects()
    pass
