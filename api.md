# 缺失修繕系統 API 文件

本文件描述系統所有 API 端點、請求格式和回應格式，供前端工程師整合使用。

## 目錄

1. [狀態流程](#狀態流程)
2. [缺失單 API](#缺失單-api)
3. [改善報告 API](#改善報告-api)
4. [確認結果 API](#確認結果-api)
5. [相片 API](#相片-api)
6. [廠商存取流程](#廠商存取流程)

## 狀態流程

缺失單狀態流程如下：
- `等待中` - 缺失已建立但未開始修繕
- `改善中` - 已指派廠商進行修繕或確認結果被退回
- `待確認` - 廠商已提交修繕結果，等待確認
- `已完成` - 修繕結果已被確認並接受
- `退件` - 缺失被取消或無需修繕

狀態轉換規則：
1. 當廠商提交修繕報告時，狀態自動從`改善中`變更為`待確認`
2. 專案擁有者或協作者確認修繕結果時：
   - 接受：狀態變更為`已完成`
   - 退回：狀態變更為`改善中`

## 缺失單 API

### 取得缺失單列表

```
GET /defects/
```

**Query Parameters**:
- `skip`: 分頁起始索引 (預設: 0)
- `limit`: 每頁筆數 (預設: 100)
- `project_id`: 專案ID (可選)
- `status`: 狀態 (可選)
- `submitter_id`: 提交者ID (可選)

**Response**: 缺失單列表

### 取得缺失單詳情

```
GET /defects/{defect_id}
```

**Path Parameters**:
- `defect_id`: 缺失ID

**Query Parameters**:
- `include_marks`: 是否包含標記 (預設: false)
- `include_photos`: 是否包含照片 (預設: false)
- `include_improvements`: 是否包含改善報告 (預設: false)
- `include_full`: 是否包含完整資料 (預設: false)

**Response**: 缺失單詳情

### 透過唯一碼取得缺失單

```
GET /defects/unique_code/{unique_code}
```

**Path Parameters**:
- `unique_code`: 缺失唯一碼

**Response**: 缺失單詳情

### 建立缺失單

```
POST /defects/
```

**Headers**:
- `X-Current-User-ID`: 當前用戶ID

**Request Body**:
```json
{
  "project_id": 1,
  "defect_category_id": 1,
  "defect_description": "描述缺失內容",
  "expected_completion_day": "2025-08-01",
  "assigned_vendor_id": 1
}
```

**Response**: 新建立的缺失單

### 更新缺失單

```
PUT /defects/{defect_id}
```

**Path Parameters**:
- `defect_id`: 缺失ID

**Headers**:
- `X-Current-User-ID`: 當前用戶ID

**Request Body**:
```json
{
  "defect_description": "更新的描述",
  "status": "改善中",
  "expected_completion_day": "2025-08-15"
}
```

**Response**: 更新後的缺失單

## 改善報告 API

### 建立改善報告

```
POST /improvements/
```

**Headers**:
- `X-Current-User-ID`: 當前用戶ID (可選)

**Request Body**:
```json
{
  "defect_id": 1,
  "content": "改善內容描述",
  "improvement_date": "2025-07-15"
}
```

**Response**: 新建立的改善報告

### 廠商透過唯一碼提交改善報告

```
POST /improvements/by-unique-code/{unique_code}
```

**Path Parameters**:
- `unique_code`: 缺失唯一碼

**Request Body**:
```json
{
  "content": "廠商提交的改善內容",
  "improvement_date": "2025-07-15"
}
```

**Response**: 新建立的改善報告

> 注意：此API無需驗證，廠商只需知道缺失的唯一碼即可提交報告。提交後，對應缺失狀態會自動更新為`待確認`。

### 取得改善報告列表

```
GET /improvements/
```

**Query Parameters**:
- `skip`: 分頁起始索引 (預設: 0)
- `limit`: 每頁筆數 (預設: 100)
- `defect_id`: 缺失ID (可選)
- `submitter_id`: 提交者ID (可選)

**Response**: 改善報告列表

### 取得改善報告詳情

```
GET /improvements/{improvement_id}
```

**Path Parameters**:
- `improvement_id`: 改善報告ID

**Response**: 改善報告詳情

### 更新改善報告

```
PUT /improvements/{improvement_id}
```

**Path Parameters**:
- `improvement_id`: 改善報告ID

**Headers**:
- `X-Current-User-ID`: 當前用戶ID

**Request Body**:
```json
{
  "content": "更新的改善內容",
  "improvement_date": "2025-07-20"
}
```

**Response**: 更新後的改善報告

> 注意：只有報告提交者可以更新改善報告

## 確認結果 API

### 建立確認結果

```
POST /confirmations/
```

**Headers**:
- `X-Current-User-ID`: 當前用戶ID

**Request Body**:
```json
{
  "improvement_id": 1,
  "status": "接受", // 可選值: "接受", "退回", "未確認"
  "comment": "確認意見",
  "confirmation_date": "2025-07-25"
}
```

**Response**: 新建立的確認結果

> 注意：
> - 當狀態為`接受`時，對應缺失狀態會自動更新為`已完成`
> - 當狀態為`退回`時，對應缺失狀態會自動更新為`改善中`

### 取得確認結果列表

```
GET /confirmations/
```

**Query Parameters**:
- `skip`: 分頁起始索引 (預設: 0)
- `limit`: 每頁筆數 (預設: 100)
- `improvement_id`: 改善報告ID (可選)
- `confirmer_id`: 確認者ID (可選)
- `status`: 確認狀態 (可選)

**Response**: 確認結果列表

### 取得確認結果詳情

```
GET /confirmations/{confirmation_id}
```

**Path Parameters**:
- `confirmation_id`: 確認結果ID

**Response**: 確認結果詳情

### 取得確認結果詳情(包含關聯資料)

```
GET /confirmations/{confirmation_id}/details
```

**Path Parameters**:
- `confirmation_id`: 確認結果ID

**Response**: 包含關聯資料的確認結果詳情

### 更新確認結果

```
PUT /confirmations/{confirmation_id}
```

**Path Parameters**:
- `confirmation_id`: 確認結果 ID

**Headers**:
- `X-Current-User-ID`: 當前用戶ID

**Request Body**:
```json
{
  "status": "接受",
  "comment": "更新的確認意見",
  "confirmation_date": "2025-07-30"
}
```

**Response**: 更新後的確認結果

> 注意：只有確認結果的確認者可以更新確認結果

## 相片 API

### 上傳相片

```
POST /photos/
```

**Request Body** (multipart/form-data):
- `file`: 相片檔案 (必需)
- `related_type`: 關聯類型 (必需，可選值: "defect", "improvement", "confirmation")
- `related_id`: 關聯項目ID (必需，如 defect_id)
- `description`: 相片描述 (可選)

**Response**: 新建立的相片資訊，包含相片的完整URL

> 注意：相片會依關聯類型分別存放在不同資料夾中

### 取得相片列表

```
GET /photos/
```

**Query Parameters**:
- `related_type`: 關聯類型 (可選，如 "defect")
- `related_id`: 關聯項目ID (可選，如 defect_id)
- `skip`: 分頁起始索引 (預設: 0)
- `limit`: 每頁筆數 (預設: 100，最大1至100)

**Response**: 相片列表，包含每張相片的詳細資訊和完整URL

### 取得相片詳情

```
GET /photos/{photo_id}
```

**Path Parameters**:
- `photo_id`: 相片ID

**Response**: 相片詳情，包含完整URL

### 更新相片資訊

```
PUT /photos/{photo_id}
```

**Path Parameters**:
- `photo_id`: 相片ID

**Request Body** (JSON):
```json
{
  "description": "更新的相片描述"
}
```

**Response**: 更新後的相片詳情，包含完整URL

### 刪除相片

```
DELETE /photos/{photo_id}
```

**Path Parameters**:
- `photo_id`: 相片ID

**Response**: 無內容回應 (204 No Content)

## 廠商存取流程

系統採用唯一碼機制，簡化廠商存取流程：

1. 缺失建立時會自動生成唯一碼(UUID)
2. 專案管理者可將含唯一碼的URL分享給廠商
3. 廠商使用唯一碼存取缺失資訊：
   ```
   GET /defects/unique_code/{unique_code}
   ```
4. 廠商完成修繕後，使用相同唯一碼提交改善報告：
   ```
   POST /improvements/by-unique-code/{unique_code}
   ```
5. 系統自動將缺失狀態更新為`待確認`
6. 專案擁有者或協作者接收通知，進行複驗

此流程無需廠商註冊或登入系統，大幅簡化操作流程。

---

## 狀態碼說明

- `200` - 請求成功
- `201` - 資源成功建立
- `204` - 請求成功但無返回內容
- `400` - 請求格式錯誤
- `401` - 未提供認證資訊
- `403` - 無權限執行操作
- `404` - 資源不存在
- `422` - 請求參數驗證失敗

## 認證說明

大部分API需要透過`X-Current-User-ID`標頭提供用戶ID進行簡單認證。
例外為透過唯一碼存取的API，如`/defects/unique_code/{unique_code}`和`/improvements/by-unique-code/{unique_code}`，這些API無需認證即可使用。
