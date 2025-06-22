import streamlit as st
import api

defect_data=api.get_defect_by_unique_code(st.session_state.defect_unique_code)

st.write(defect_data)

st.markdown("---")

defect_detail=api.get_defect(defect_data['defect_id'],with_full_related=True)

st.write(defect_detail)

st.markdown("---")



# # 初始化 session state 變數
# def init_repair_session_state():
#     # 檢查是否有缺失的唯一碼
#     if "defect_unique_code" not in st.session_state:
#         st.error("未提供缺失唯一碼，無法進行修繕")
#         return False
    
#     # 初始化修繕表單相關的 session state 變數
#     if "repair_description" not in st.session_state:
#         st.session_state.repair_description = ""
#     if "repair_images" not in st.session_state:
#         st.session_state.repair_images = []
#     if "repair_image_files" not in st.session_state:
#         st.session_state.repair_image_files = []
#     if "defect_data" not in st.session_state:
#         # 從 API 獲取缺失詳情
#         defect_data = api.get_defect_by_unique_code(st.session_state.defect_unique_code)
#         if not defect_data:
#             st.error(f"找不到唯一碼為 {st.session_state.defect_unique_code} 的缺失")
#             return False
#         st.session_state.defect_data = defect_data
    
#     return True

# # 顯示缺失詳情
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
