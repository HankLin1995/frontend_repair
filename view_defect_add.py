import streamlit as st
import api
from PIL import Image, ImageDraw
import io
import requests
from streamlit_antd_components import steps
from datetime import datetime
from streamlit_image_coordinates import streamlit_image_coordinates
from streamlit_extras.floating_button import floating_button
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit_antd_components as sac
import time

default_session_state = {
    "basemap_id": None,
    "basemap_mark_X": None,
    "basemap_mark_Y": None,
    "before_number": None,
    "defect_description": None,
    "defect_category": None,
    "defect_category_id": None,
    "assigned_vendor": None,
    "assigned_vendor_id": None,
    "expected_date": None,
    "defect_images": [],
}

for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# st.sidebar.json(st.session_state)

@st.dialog("新增缺失分類")
def create_project_category():
    with st.container(border=True):
        category_name = st.text_input("分類名稱")
        description = st.text_area("描述",value="無")
        if st.button("新增分類"):
            if not category_name:
                st.warning("請輸入分類名稱")
                return
            try:
                result = api.create_defect_category(st.session_state.active_project_id,category_name,description)
                if result:
                    st.success(f"分類 '{category_name}' 已新增")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"新增分類時發生錯誤: {str(e)}")

@st.dialog("新增廠商")
def create_vendor():
    with st.container(border=True):
        vendor_name = st.text_input("廠商名稱")
        contact_person = st.text_input("聯絡人")
        phone = st.text_input("電話")
        email=st.text_input("電子郵件")
        line_id=st.text_input("Line ID")
        responsibilities = st.text_input("負責範圍")
        submit_button = st.button("新增廠商")
        
        if submit_button:
            if not vendor_name:
                st.warning("請輸入廠商名稱")
                return
            
            try:
                result = api.create_vendor(st.session_state.active_project_id,vendor_name, contact_person, phone, email , line_id , responsibilities)
                if result:
                    st.success(f"廠商 '{vendor_name}' 已新增")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"新增廠商時發生錯誤: {str(e)}")


def get_selectbox_index(session_value, options_list, options_dict):
    if session_value in options_list:
        return options_list.index(session_value)
    else:
        current_id = str(session_value)
        current_name = None
        for k, v in options_dict.items():
            if str(v) == current_id:
                current_name = k
                break
        if current_name and current_name in options_list:
            return options_list.index(current_name)
    return 0

def draw_basemap_with_marker(image_url, x, y, radius=15):
    """
    下載底圖並在 (x, y) 畫紅圈，回傳 PIL Image
    """
    resp = requests.get(image_url)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    if x is not None and y is not None:
        draw = ImageDraw.Draw(img)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=4)
    return img

def display_basemap_add(basemaps):
    # 建立名稱對 id 的 dict
    basemap_name_to_id = {b['map_name']: b['base_map_id'] for b in basemaps}
    options = ["請選擇"] + list(basemap_name_to_id.keys())
    # 用 get_selectbox_index 取得 index，session_state.basemap_id 為 id
    index = get_selectbox_index(st.session_state.basemap_id, options, basemap_name_to_id)
    selected_base_map = st.selectbox("選擇底圖", options=options, index=index)
    selected_base_map_id = basemap_name_to_id.get(selected_base_map)
    if selected_base_map != "請選擇":
        selected_map_data = next((b for b in basemaps if b['map_name'] == selected_base_map), None)
        if selected_map_data:
            image_url = "http://localhost:8000/" + selected_map_data['file_path']

            # 使用共用函式取得已標記圖片
            x = st.session_state.basemap_mark_X
            y = st.session_state.basemap_mark_Y
            img = draw_basemap_with_marker(image_url, x, y, radius=15)
            value = streamlit_image_coordinates(img)
            if value:
                st.toast(f"標示位置: X={value['x']}, Y={value['y']}", icon="📍")
                st.session_state.basemap_mark_X = value['x']
                st.session_state.basemap_mark_Y = value['y']
                st.session_state.basemap_id = selected_base_map_id
                st.rerun()

def display_defect_add(category_options,vendor_options):

    st.markdown("#### 基本資料")

    if st.session_state.before_number:
        before_number=st.text_input("前置缺失編號",value=st.session_state.before_number)
    else:
        before_number=st.text_input("前置缺失編號")

    if before_number=="":
        before_number=None

    if st.session_state.defect_description:
        defect_description = st.text_area("缺失描述",value=st.session_state.defect_description)
    else:
        defect_description = st.text_area("缺失描述")

    col3, col4 = st.columns([2, 1])

    # 準備 options list
    category_options_list = ["(無)" if not category_options else "請選擇"] + list(category_options.keys())
    vendor_options_list = ["(無)" if not vendor_options else "請選擇"] + list(vendor_options.keys())

    with col3:
        if st.session_state.defect_category:
            category_index = get_selectbox_index(st.session_state.defect_category, category_options_list, category_options)
            defect_category = st.selectbox("缺失分類", options=category_options_list, index=category_index)
        else:
            defect_category = st.selectbox("缺失分類", options=category_options_list)

        defect_category_id = category_options.get(defect_category)
    with col4:
        add_vertical_space(2)
        if st.button("找不到分類?"):
            create_project_category()

    col5, col6 = st.columns([2, 1])

    with col5:
        if st.session_state.assigned_vendor:
            vendor_index = get_selectbox_index(st.session_state.assigned_vendor, vendor_options_list, vendor_options)
            assigned_vendor = st.selectbox("指派廠商", options=vendor_options_list, index=vendor_index)
        else:
            assigned_vendor = st.selectbox("指派廠商", options=vendor_options_list)
        assigned_vendor_id = vendor_options.get(assigned_vendor)
    with col6:
        add_vertical_space(2)
        if st.button("找不到廠商?"):
            create_vendor()


    if st.session_state.expected_date:
        expected_date=st.date_input("預計改善日期",value=st.session_state.expected_date)
    else:
        expected_date=st.date_input("預計改善日期")

    st.session_state.before_number=before_number
    st.session_state.defect_description=defect_description
    st.session_state.defect_category=defect_category
    st.session_state.defect_category_id=defect_category_id
    st.session_state.assigned_vendor=assigned_vendor
    st.session_state.assigned_vendor_id=assigned_vendor_id
    st.session_state.expected_date=expected_date


def display_defect_result():
    ### 標記、描述、照片

    col1,col2=st.columns([1,2])

    with col2:
        st.markdown("#### 🗺️ 底圖標記")
        basemap = api.get_basemap(st.session_state.basemap_id)
        # show image with red circle
        image_url = "http://localhost:8000/" + basemap['file_path']

        # 使用共用函式取得已標記圖片
        x = st.session_state.basemap_mark_X
        y = st.session_state.basemap_mark_Y
        img = draw_basemap_with_marker(image_url, x, y, radius=15)
        st.image(img, caption=f"**座標：** X = `{st.session_state.basemap_mark_X}`, Y = `{st.session_state.basemap_mark_Y}`")

    with col1:
        st.markdown("#### 📝 缺失描述")
        with st.container(border=True):
            st.markdown(f"**🔢 前置缺失編號：** {st.session_state.before_number or '—'}")
            st.markdown(f"**📝 缺失描述：** {st.session_state.defect_description or '—'}")
            st.markdown(f"**🏷️ 缺失分類：** {st.session_state.defect_category or '—'}")
            st.markdown(f"**🏭 指派廠商：** {st.session_state.assigned_vendor or '—'}")
            st.markdown(f"**📅 預計改善日期：** {st.session_state.expected_date.strftime('%Y-%m-%d') if st.session_state.expected_date else '—'}")

    st.markdown("#### 📷 缺失照片")
    img_cols = st.columns(3)
    for i, file in enumerate(st.session_state.defect_images):
        with img_cols[i % 3]:
            st.image(file)


def main(basemaps):
    
    # 初始化 current_step
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    
    # 步驟進度條
    current_step = sac.steps(
        items=[
            sac.StepsItem(title='底圖標示'),
            sac.StepsItem(title='缺失描述'),
            sac.StepsItem(title='上傳照片'),
            sac.StepsItem(title='確認內容'),
        ],
        format_func='title',
        index=st.session_state.current_step,
        return_index=True,
    )
    
    # 更新 current_step 如果用戶點擊了步驟
    if current_step != st.session_state.current_step:
        st.session_state.current_step = current_step
        st.rerun()

    with st.container(border=True):
        submitted = False
        
        if current_step == 0:
            display_basemap_add(basemaps)

        elif current_step == 1:
            # st.subheader('缺失描述')
            display_defect_add(category_options,vendor_options)

        elif current_step == 2:
            # st.subheader('上傳照片')
            files= st.file_uploader("上傳缺失照片", type=["png", "jpg", "jpeg"],accept_multiple_files=True)

            if files:
                st.session_state.defect_images = files

            cols = st.columns(3)
            for i, file in enumerate(st.session_state.defect_images):
                with cols[i % 3]:
                    st.image(file)
            
        elif current_step == 3:

            display_defect_result()

        # 表單按鈕
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_step > 0:
                if st.button('上一步', use_container_width=True):
                    st.session_state.current_step -= 1
                    st.rerun()
        
        with col2:
            if st.session_state.current_step < 3:
                if st.button('下一步', use_container_width=True):
                    st.session_state.current_step += 1
                    st.rerun()
            elif st.session_state.current_step == 3:
                submit_button = st.button('提交表單', use_container_width=True, type='primary')
                if submit_button:

                    # 將日期物件轉為 yyyy-mm-dd 字串
                    expected_date = st.session_state.expected_date
                    if expected_date is not None and hasattr(expected_date, "isoformat"):
                        expected_date = expected_date.isoformat()

                    defect_data = {
                        "defect_description": st.session_state.defect_description,
                        "defect_category_id": st.session_state.defect_category_id,
                        "assigned_vendor_id": st.session_state.assigned_vendor_id,
                        "expected_completion_day": expected_date,
                        # "expected_completion_day": st.session_state.expected_day_count,
                        "previous_defect_id": st.session_state.before_number,
                        "status": "改善中",
                    }

                    st.write(defect_data)

                    # st.write(defect_data)

                    res=api.create_defect(st.session_state.active_project_id, 1, defect_data)

                    if 'defect_id' in res:
                        st.toast("缺失描述新增成功!",icon= "✅")

                        defect_mark_data={
                            # "defect_mark_id": res['defect_id'],
                            "defect_id": res['defect_id'],
                            "base_map_id": st.session_state.basemap_id,
                            "coordinate_x": st.session_state.basemap_mark_X,
                            "coordinate_y": st.session_state.basemap_mark_Y,
                            "scale": 1.0
                        }

                        res2=api.create_defect_mark(defect_mark_data)
                        
                        # st.write(res2)

                        if 'defect_mark_id' in res2:
                            st.toast("缺失標記新增成功!",icon= "✅")

                        for image_file in st.session_state.defect_images:
                            # 這裡 image_file 應該是 UploadedFile 物件
                            file_tuple = (image_file.name, image_file, image_file.type)
                            res3 = api.upload_defect_image(res['defect_id'], file_tuple)
                            
                            if 'photo_id' in res3:
                                st.toast("缺失照片新增成功!",icon= "✅")
                    
                    else:
                        st.warning(res)




#========MAIN UI========

project = api.get_project(st.session_state.active_project_id)

if project:

    st.caption("工程 / "+project['project_name']+" / 缺失表單")

    # --- Fetch defect categories and vendors ---
    categories = api.get_defect_categories()
    vendors = api.get_vendors()

    category_options = {str(c.get('name', c.get('category_name', '無分類'))): c['defect_category_id'] for c in categories} if categories else {}
    vendor_options = {str(v.get('vendor_name', '無廠商')): v['vendor_id'] for v in vendors} if vendors else {}

    basemaps=api.get_basemaps(st.session_state.active_project_id)

    main(basemaps)
else:
    st.warning("請先至工程列表選擇當前工程!")
    st.stop()
