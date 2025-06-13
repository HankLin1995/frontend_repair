# CATEGORY LIST
# 門窗、木作、美容
# 防水工程
# 泥作、油漆、石材
# 連續壁滲水
# 健身設備、停車設備、鐵件
# 弱電工程
# 衛浴設備、淋浴間、廚具
# 消防工程、給排水、汙水
# 空調、流瀑、垃圾室、電氣工程
# 設計規劃、使用問題

import requests

BASE_URL = "http://localhost:8000"

list_category=[
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

data={
    "category_name": None,
    "project_id": 1,
    "description": None
}

for i in list_category:
    data['category_name']=i
    response = requests.post(f"{BASE_URL}/defect-categories/", json=data)
    print(response.json())