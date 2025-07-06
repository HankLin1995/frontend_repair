import streamlit as st
import api
from utils import draw_basemap_with_marker
import datetime
import time

defect_data=api.get_defect_by_unique_code(st.session_state.defect_unique_code)

if defect_data['status'] != '改善中':
    st.error("無法修繕，因為狀態不是改善中")
    st.stop()

# st.write(defect_data)

# st.markdown("---")

defect_detail=api.get_defect(defect_data['defect_id'],with_photos=True,with_marks=True,with_full_related=True)

# st.sidebar.json(defect_detail)


with st.expander("🔢 缺失詳情",expanded=True):
    # st.markdown(f"**🔢 前置缺失編號：** {defect_detail['previous_defect_id'] or '—'}")
    st.markdown(f"**📍 位置：** {defect_detail['location'] or '—'}")
    st.markdown(f"**📝 缺失描述：** {defect_detail['defect_description'] or '—'}")
    # st.markdown(f"**🏷️ 缺失分類：** {defect_detail['category_name'] or '—'}")
    st.markdown(f"**🏭 指派廠商：** {defect_detail['assigned_vendor_name'] or '—'}")
    # 只顯示日期部分
    import pandas as pd
    created_at = defect_detail['created_at']
    if created_at:
        date_str = pd.to_datetime(created_at).strftime('%Y-%m-%d')
        st.markdown(f"**📅創建日期：** {date_str}")
    else:
        st.markdown("**📅創建日期：** —")
    # st.markdown(f"**🏭 責任廠商：** {defect_detail['responsible_vendor_name'] or '—'}")
    # st.markdown(f"**📅 預計改善日期：** {defect_detail['expected_completion_date'].strftime('%Y-%m-%d') if defect_detail['expected_completion_date'] else '—'}")

with st.expander("📷缺失照片"):
    img_cols = st.columns(3)
    if defect_detail['photos']: 
        for i, file in enumerate(defect_detail['photos']):
            with img_cols[i % 3]:
                st.image("http://localhost:8000"+file['image_url'])
    else:
        st.info("無缺失照片")

with st.expander("📍缺失標記"):
    try:
        base_map=api.get_basemap(defect_detail['defect_marks'][0]['base_map_id'])
        base_map_image="http://localhost:8000/"+base_map['file_path']

        x = defect_detail['defect_marks'][0]['coordinate_x']
        y = defect_detail['defect_marks'][0]['coordinate_y']
        img = draw_basemap_with_marker(base_map_image, x, y, radius=15)
        st.image(img, caption=f"**座標：** X = `{x}`, Y = `{y}`")
    except:
        st.error("無法顯示缺失標記")        

    

with st.container(border=True):
    repair_note=st.text_area("修繕說明")
    repair_images=st.file_uploader("上傳修繕照片",accept_multiple_files=True)

    if st.button("確認修繕",type="primary",use_container_width=True):
        if not repair_note:
            st.error("請輸入修繕說明")
        else:
            # 獲取當前日期作為改善日期
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # 使用唯一碼提交改善報告
            with st.spinner("正在提交改善報告..."):
                result = api.create_improvement_by_unique_code(
                    unique_code=st.session_state.defect_unique_code,
                    content=repair_note,
                    improvement_date=today
                )
                
                if result:
                    # 上傳修繕照片
                    if repair_images:
                        with st.spinner("正在上傳修繕照片..."):
                            for img in repair_images:
                                api.upload_defect_image(
                                    defect_id=result['improvement_id'],
                                    image_file=img,
                                    description="修繕照片",
                                    related_type="improvement"
                                )
                    
                    st.success("修繕資訊已成功提交！")
                    time.sleep(3)
                    st.balloons()
                    # 重新載入頁面以顯示最新資訊
                    st.rerun()
                else:
                    st.error("提交改善報告失敗，請稍後再試")


# def display_defect_details():
#     defect = st.session_state.defect_data
#     defect_detail=api.get_defect(defect['defect_id'],with_full_related=True)
    
#     st.write(defect_detail)

#     # # 創建兩列佈局
#     # col1, col2 = st.columns([2, 1])
    
#     # with col1:
#     #     st.subheader("缺失詳情")
#     #     # st.markdown(f"**缺失唯一碼:** {defect.get('unique_code', '未知')}")
#     #     st.markdown(f"**缺失描述:** {defect.get('defect_description', '未提供描述')}")
        
#     #     # 顯示分類和廠商
#     #     category = defect.get('defect_category', {})
#     #     vendor = defect.get('assigned_vendor', {})
        
#     #     if category:
#     #         st.markdown(f"**缺失分類:** {category.get('category_name', '未分類')}")
        
#     #     if vendor:
#     #         st.markdown(f"**負責廠商:** {vendor.get('vendor_name', '未指派廠商')}")
        
#     #     # 顯示預計完成日期和狀態
#     #     st.markdown(f"**預計完成日期:** {defect.get('expected_completion_date', '未設定')}")
        
#     #     status = defect.get('status', '未知')
#     #     status_color = "red"
#     #     if status == "已修繕":
#     #         status_color = "green"
#     #     elif status == "修繕中":
#     #         status_color = "orange"
        
#     #     st.markdown(f"**目前狀態:** <span style='color:{status_color};'>{status}</span>", unsafe_allow_html=True)
    
#     # with col2:
#     #     st.subheader("缺失照片")
#     #     # 獲取並顯示缺失照片
#     #     # 這裡假設 API 返回的缺失數據中包含照片信息
#     #     photos = defect.get('photos', [])
#     #     if photos:
#     #         for photo in photos:
#     #             # 假設 photo 包含 image_url 或類似字段
#     #             image_url = photo.get('image_url', '')
#     #             if image_url:
#     #                 st.image(image_url, caption=photo.get('description', ''), use_column_width=True)
#     #     else:
#     #         st.info("無缺失照片")

# # 修繕表單
# def repair_form():
#     st.subheader("修繕資訊")
    
#     # 修繕描述
#     st.session_state.repair_description = st.text_area(
#         "修繕描述", 
#         value=st.session_state.repair_description,
#         height=150,
#         placeholder="請輸入修繕描述..."
#     )
    
#     # 上傳修繕照片
#     uploaded_files = st.file_uploader(
#         "上傳修繕照片", 
#         accept_multiple_files=True,
#         type=["jpg", "jpeg", "png"]
#     )
    
#     # 處理上傳的照片
#     if uploaded_files:
#         new_images = []
#         new_image_files = []
        
#         for file in uploaded_files:
#             # 檢查是否已經在列表中
#             if file.name not in [img.name for img in st.session_state.repair_images]:
#                 # 讀取圖片並添加到列表
#                 image = Image.open(file)
#                 new_images.append(file)
                
#                 # 保存文件內容以便後續上傳
#                 file_bytes = io.BytesIO()
#                 file.seek(0)
#                 file_bytes.write(file.read())
#                 file_bytes.seek(0)
#                 new_image_files.append((file.name, file_bytes, file.type))
        
#         # 更新 session state
#         st.session_state.repair_images.extend(new_images)
#         st.session_state.repair_image_files.extend(new_image_files)
    
#     # 顯示已上傳的照片
#     if st.session_state.repair_images:
#         st.subheader("已上傳的修繕照片")
#         cols = st.columns(3)
#         for i, img in enumerate(st.session_state.repair_images):
#             with cols[i % 3]:
#                 st.image(img, caption=img.name, use_column_width=True)
                
#                 # 添加刪除按鈕
#                 if st.button(f"刪除 {img.name}", key=f"del_{i}"):
#                     st.session_state.repair_images.pop(i)
#                     st.session_state.repair_image_files.pop(i)
#                     st.rerun()
    
#     # 提交按鈕
#     if st.button("提交修繕資訊", type="primary"):
#         submit_repair()

# # 提交修繕資訊
# def submit_repair():
#     # 檢查是否有修繕描述
#     if not st.session_state.repair_description:
#         st.error("請輸入修繕描述")
#         return
    
#     # 獲取缺失 ID
#     defect_id = st.session_state.defect_data.get('defect_id')
#     if not defect_id:
#         st.error("無法獲取缺失 ID")
#         return
    
#     # 更新缺失狀態為「已修繕」
#     update_data = {
#         "repair_description": st.session_state.repair_description,
#         "status": "已修繕"
#     }
    
#     with st.spinner("正在更新缺失資訊..."):
#         # 更新缺失
#         updated_defect = api.update_defect(defect_id, update_data)
#         if not updated_defect:
#             st.error("更新缺失資訊失敗")
#             return
        
#         # 上傳修繕照片
#         if st.session_state.repair_image_files:
#             with st.spinner("正在上傳修繕照片..."):
#                 for img_file in st.session_state.repair_image_files:
#                     api.upload_defect_image(defect_id, img_file, "修繕照片")
        
#         # 更新 session state 中的缺失數據
#         st.session_state.defect_data = api.get_defect_by_unique_code(st.session_state.defect_unique_code)
        
#         # 清除修繕表單數據
#         st.session_state.repair_description = ""
#         st.session_state.repair_images = []
#         st.session_state.repair_image_files = []
        
#         # 顯示成功訊息
#         st.success("修繕資訊已成功提交！")
#         time.sleep(2)
#         st.rerun()

# # 主函數
# def show_defect_repair():
#     # st.title("缺失修繕頁面")
    
#     # 初始化 session state
#     if not init_repair_session_state():
#         return
    
#     # 顯示缺失詳情
#     display_defect_details()
    
#     # 分隔線
#     st.markdown("---")
    
#     # 顯示修繕表單
#     repair_form()

# # 當直接運行此文件時
# if __name__ == "__main__":
#     show_defect_repair()
