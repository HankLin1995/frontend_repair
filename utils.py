def format_datetime(dt_str):
    """Format datetime string for display"""
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        return dt_str

def get_status_class(status):
    if status == '已完成':
        return '🟢 已完成'
    elif status == '改善中':
        return '🟡 改善中'
    elif status == '已取消':
        return '🔴 已取消'
    elif status == '等待中':
        return '⚪ 等待中'
    elif status == '待確認':
        return '🟣 待確認'
    else:
        return '🟤 未設定'

def get_urgency_class(days):
    try:
        days = int(days)
        if days <= 0:
            return '🟥 '  # 已逾期
        elif days <= 7:
            return '🟨 '  # 緊急
        elif days <= 14:
            return '🟩 '  # 待處理
        # elif days < 999:
        #     return '🟩 '  # 未開始
        else:
            return '⬜️ '  # 未設定
    except:
        return '❔ '  # 無法辨識

def draw_basemap_with_marker(image_url, x, y, radius=15):

    import requests
    from PIL import Image, ImageDraw
    import io

    """
    下載底圖並在 (x, y) 畫紅圈，回傳 PIL Image
    """
    resp = requests.get(image_url)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    if x is not None and y is not None:
        draw = ImageDraw.Draw(img)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline="red", width=4)
    return img
