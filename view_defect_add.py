import streamlit as st
import api
from datetime import datetime

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
                result = api.create_defect_category(category_name,description)
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
                result = api.create_vendor(vendor_name, contact_person, phone, email , line_id , responsibilities)
                if result:
                    st.success(f"廠商 '{vendor_name}' 已新增")
                    st.rerun()
                else:
                    st.error("API 返回失敗結果")
            except Exception as e:
                st.error(f"新增廠商時發生錯誤: {str(e)}")


project = api.get_project(st.session_state.active_project_id)

st.markdown("#### 工程 / "+project['project_name']+" / 新增缺失")
st.markdown("---")

# --- Fetch defect categories and vendors ---
categories = api.get_defect_categories()
vendors = api.get_vendors()

category_options = {str(c.get('name', c.get('category_name', '無分類'))): c['defect_category_id'] for c in categories} if categories else {}
vendor_options = {str(v.get('vendor_name', '無廠商')): v['vendor_id'] for v in vendors} if vendors else {}

col1,col2=st.columns([1,1])

with col1:

    with st.container(border=True):

        st.markdown("#### 基本資料")

        defect_description = st.text_area("缺失描述", max_chars=300)

        col3,col4=st.columns([2,1])

        with col3:
            defect_category = st.selectbox("缺失分類", options=["(無)" if not category_options else "請選擇"] + list(category_options.keys()))
        with col4:
            if st.button("找不到分類?"):
                create_project_category()

        col5,col6=st.columns([2,1])

        with col5:
            assigned_vendor = st.selectbox("指派廠商", options=["(無)" if not vendor_options else "請選擇"] + list(vendor_options.keys()))
        with col6:
            if st.button("找不到廠商?"):
                create_vendor()

        expected_date=st.date_input("預計改善日期")

        files= st.file_uploader("上傳缺失照片", type=["png", "jpg", "jpeg"],accept_multiple_files=True)

        st.markdown("---")

        if st.button("送出缺失",type="primary"):
            # Prepare payload
            payload = {
                "project_id": st.session_state.active_project_id,
                "submitted_id": st.session_state.user_id,
                "defect_description": defect_description,
            }
            if defect_category not in ["(無)", "請選擇"]:
                payload["defect_category_id"] = category_options[defect_category]
            if assigned_vendor not in ["(無)", "請選擇"]:
                payload["assigned_vendor_id"] = vendor_options[assigned_vendor]
            payload["expected_date"] = expected_date.strftime("%Y-%m-%d")
            # Call API
            result = api.create_defect(**payload)
            if result and not result.get("error"):
                st.success("缺失已成功新增！")
                st.balloons()
            else:
                st.error(f"新增失敗: {result.get('error', '未知錯誤')}")

with col2:

    with st.container(border=True):

        st.markdown("#### 圖片預覽")

        cols = st.columns(2)
        
        for i, file in enumerate(files):
            with cols[i % 2]:
                # with st.container(border=True):
                st.image(file)
        

        # from streamlit_carousel import carousel
    # from PIL import Image
    # import io

    # preview_items = []
    # if files:
    #     for file in files:
    #         try:
    #             img = Image.open(file)
    #             # 中心裁切成 1024x648
    #             target_w, target_h = 1024, 648
    #             target_ratio = target_w / target_h
    #             w, h = img.size
    #             img_ratio = w / h
    #             if img_ratio > target_ratio:
    #                 crop_h = h
    #                 crop_w = int(h * target_ratio)
    #             else:
    #                 crop_w = w
    #                 crop_h = int(w / target_ratio)
    #             left = (w - crop_w) // 2
    #             top = (h - crop_h) // 2
    #             right = left + crop_w
    #             bottom = top + crop_h
    #             cropped_img = img.crop((left, top, right, bottom)).resize((target_w, target_h), Image.LANCZOS)
    #             # 轉 base64
    #             buf = io.BytesIO()
    #             cropped_img.save(buf, format="JPEG")
    #             img_bytes = buf.getvalue()
    #             import base64
    #             img_b64 = base64.b64encode(img_bytes).decode()
    #             img_url = f"data:image/jpeg;base64,{img_b64}"
    #             preview_items.append({
    #                 "title": file.name,
    #                 "text": f"{file.name}",
    #                 "img": img_url
    #             })
    #         except Exception as e:
    #             preview_items.append({
    #                 "title": file.name,
    #                 "text": f"圖片預覽失敗: {e}",
    #                 "img": "https://placehold.co/600x400?text=預覽失敗"
    #             })
    # else:
    #     preview_items = [
    #         dict(
    #             title="尚未上傳圖片",
    #             text="請於左側選擇圖片後預覽",
    #             img="https://placehold.co/600x400?text=No+Image"
    #         )
    #     ]

    # carousel(items=preview_items)

    
