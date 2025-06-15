import requests
import random
from datetime import datetime, timedelta
import api
import os

# Base URL for the API
BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')

# 缺失分類列表
CATEGORIES = [
    "門窗、木作、美容",
    "防水工程",
    "泥作、油漆、石材",
    "連續壁滲水",
    "健身設備、停車設備、鐵件",
    "弱電工程",
    "衛浴設備、淋浴間、廚具",
    "消防工程、給排水、汙水",
    "空調、流瀑、垃圾室、電氣工程",
    "設計規劃、使用問題"
]

# 廠商列表
VENDORS = [
    {
        "vendor_name": "台灣營建工程有限公司",
        "contact_person": "張志明",
        "phone": "0912-345-678",
        "email": "chang@twconstruct.com",
        "line_id": "twconstruct",
        "responsibilities": "門窗、木作"
    },
    {
        "vendor_name": "永盛防水工程行",
        "contact_person": "林美玲",
        "phone": "0922-123-456",
        "email": "lin@waterproof.com",
        "line_id": "waterproof_lin",
        "responsibilities": "防水工程"
    },
    {
        "vendor_name": "大鴻泥作工程行",
        "contact_person": "王大明",
        "phone": "0933-567-890",
        "email": "wang@dahong.com",
        "line_id": "dahong_wang",
        "responsibilities": "泥作、油漆、石材"
    },
    {
        "vendor_name": "宏達設備工程有限公司",
        "contact_person": "李小華",
        "phone": "0955-789-012",
        "email": "lee@hongda.com",
        "line_id": "hongda_lee",
        "responsibilities": "健身設備、停車設備、鐵件"
    },
    {
        "vendor_name": "智慧弱電系統有限公司",
        "contact_person": "陳智偉",
        "phone": "0977-234-567",
        "email": "chen@smartsys.com",
        "line_id": "smartsys_chen",
        "responsibilities": "弱電工程"
    },
    {
        "vendor_name": "衛浴世家企業有限公司",
        "contact_person": "黃麗華",
        "phone": "0988-345-678",
        "email": "huang@bathroom.com",
        "line_id": "bathroom_huang",
        "responsibilities": "衛浴設備、淋浴間、廚具"
    },
    {
        "vendor_name": "安全消防工程有限公司",
        "contact_person": "吳安全",
        "phone": "0910-456-789",
        "email": "wu@safefire.com",
        "line_id": "safefire_wu",
        "responsibilities": "消防工程、給排水、汙水"
    },
    {
        "vendor_name": "冷暖空調有限公司",
        "contact_person": "蔡冷暖",
        "phone": "0923-567-890",
        "email": "tsai@hvac.com",
        "line_id": "hvac_tsai",
        "responsibilities": "空調、電氣工程"
    }
]

# 缺失描述範本
DEFECT_DESCRIPTIONS = [
    "牆面出現裂縫，長度約30公分",
    "天花板漏水痕跡明顯",
    "地板磁磚破損，需要更換",
    "窗戶無法正常關閉",
    "門把鬆動，使用時有異響",
    "衛浴間排水不良，容易積水",
    "牆面油漆剝落",
    "插座無法正常使用",
    "燈具故障，無法開啟",
    "冷氣出風口有異味",
    "熱水器無法正常運作",
    "廚房水龍頭漏水",
    "浴室鏡面有裂痕",
    "防火門無法自動關閉",
    "樓梯扶手鬆動",
    "電梯按鈕失靈",
    "停車場地面龜裂",
    "公共區域照明不足",
    "安全門警報系統故障",
    "監視器畫面模糊不清"
]

def create_categories(project_id=1):
    """
    創建缺失分類
    
    Args:
        project_id: 專案ID
        
    Returns:
        創建的分類列表
    """
    print("開始創建缺失分類...")
    created_categories = []
    
    for category_name in CATEGORIES:
        description = f"{category_name}相關問題"
        try:
            result = api.create_defect_category(project_id, category_name, description)
            if result:
                print(f"成功創建分類: {category_name}")
                created_categories.append(result)
            else:
                print(f"創建分類失敗: {category_name}")
        except Exception as e:
            print(f"創建分類時發生錯誤: {str(e)}")
    
    print(f"完成創建 {len(created_categories)} 個分類")
    return created_categories

def create_vendors(project_id=1):
    """
    創建廠商資料
    
    Args:
        project_id: 專案ID
        
    Returns:
        創建的廠商列表
    """
    print("開始創建廠商資料...")
    created_vendors = []
    
    for vendor_data in VENDORS:
        try:
            result = api.create_vendor(
                project_id,
                vendor_data["vendor_name"],
                vendor_data["contact_person"],
                vendor_data["phone"],
                vendor_data["email"],
                vendor_data["line_id"],
                vendor_data["responsibilities"]
            )
            if result:
                print(f"成功創建廠商: {vendor_data['vendor_name']}")
                created_vendors.append(result)
            else:
                print(f"創建廠商失敗: {vendor_data['vendor_name']}")
        except Exception as e:
            print(f"創建廠商時發生錯誤: {str(e)}")
    
    print(f"完成創建 {len(created_vendors)} 個廠商")
    return created_vendors

def create_defects(project_id=1, count=20):
    """
    創建缺失資料
    
    Args:
        project_id: 專案ID
        count: 要創建的缺失數量
        
    Returns:
        創建的缺失列表
    """
    print("開始創建缺失資料...")
    created_defects = []
    
    # 獲取現有的分類和廠商
    categories = api.get_defect_categories()
    vendors = api.get_vendors()
    
    if not categories or not vendors:
        print("無法獲取分類或廠商資料，請先創建分類和廠商")
        return []
    
    # 獲取底圖
    basemaps = api.get_basemaps(project_id)
    if not basemaps:
        print("無法獲取底圖資料，請先上傳底圖")
        return []
    
    for i in range(count):
        try:
            # 隨機選擇分類和廠商
            category = random.choice(categories)
            vendor = random.choice(vendors)
            basemap = random.choice(basemaps)
            
            # 隨機生成預期完成日期（1-30天內）
            future_date = datetime.now() + timedelta(days=random.randint(1, 30))
            # 只保留日期部分，去掉時間部分
            expected_date = future_date.date().isoformat()
            
            # 隨機選擇缺失描述
            defect_description = random.choice(DEFECT_DESCRIPTIONS)
            
            # 創建缺失資料
            defect_data = {
                "defect_description": defect_description,
                "defect_category_id": category["defect_category_id"],
                "assigned_vendor_id": vendor["vendor_id"],
                "expected_completion_day": expected_date,  # 已修正為只有日期部分
                "previous_defect_id": None,
                "status": "改善中",
            }
            
            # 創建缺失
            result = api.create_defect(project_id, 1, defect_data)
            
            if 'defect_id' in result:
                print(f"成功創建缺失 #{i+1}: {defect_description[:20]}...")
                
                # # 創建缺失標記
                # defect_mark_data = {
                #     "defect_id": result['defect_id'],
                #     "base_map_id": basemap["base_map_id"],
                #     "coordinate_x": random.randint(50, 950),
                #     "coordinate_y": random.randint(50, 550),
                #     "scale": 1.0
                # }
                
                # mark_result = api.create_defect_mark(defect_mark_data)
                # if 'defect_mark_id' in mark_result:
                #     print(f"成功創建缺失標記 #{i+1}")
                
                created_defects.append(result)
            else:
                print(f"創建缺失失敗 #{i+1}")
        except Exception as e:
            print(f"創建缺失時發生錯誤: {str(e)}")
    
    print(f"完成創建 {len(created_defects)} 個缺失")
    return created_defects

def generate_all_fake_data(project_id=1, defect_count=20):
    """
    生成所有假資料（分類、廠商、缺失）
    
    Args:
        project_id: 專案ID
        defect_count: 要創建的缺失數量
        
    Returns:
        創建的資料摘要
    """
    print(f"開始為專案 {project_id} 生成假資料...")
    
    # 創建分類
    categories = create_categories(project_id)
    
    # 創建廠商
    vendors = create_vendors(project_id)
    
    # 創建缺失
    defects = create_defects(project_id, defect_count)
    
    summary = {
        "categories_created": len(categories),
        "vendors_created": len(vendors),
        "defects_created": len(defects)
    }
    
    print(f"假資料生成完成！摘要: {summary}")
    return summary

# 如果直接執行此檔案，則生成所有假資料
if __name__ == "__main__":
    project_id = 1  # 預設專案ID
    defect_count = 30  # 預設缺失數量
    
    generate_all_fake_data(project_id, defect_count)