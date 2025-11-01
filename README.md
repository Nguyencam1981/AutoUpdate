# AutoUpdate (Python webhook receiver)

Ứng dụng mẫu nhận webhook từ GitHub và chạy script cập nhật (PowerShell) trên máy Windows.

## Tổng quan
- Server Flask nhận GitHub webhook (endpoint `/webhook`).
- Xác thực request bằng `X-Hub-Signature-256` và `GITHUB_WEBHOOK_SECRET` (HMAC SHA256).
- Khi nhận `push` hoặc `release`, server sẽ gọi `updater/updater.ps1` (PowerShell) để pull và (tuỳ chọn) restart service.

## Yêu cầu
- Windows với PowerShell và Git cài đặt.
- Python 3.8+

## Cài đặt
1. Tạo virtualenv và cài dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Cấu hình biến môi trường (PowerShell):

```powershell
$env:GITHUB_WEBHOOK_SECRET = "your_secret_here"
$env:REPO_PATH = "D:\Path\To\Your\Repo"
$env:SERVICE_NAME = "OptionalServiceNameToRestart"
```

3. Chạy server:

```powershell
python webhook_receiver\app.py
```

Server sẽ lắng nghe trên port 8000 theo mặc định.

## Cấu hình webhook trên GitHub
- URL: `http://<your-host>:8000/webhook` (hoặc dùng ngrok khi chạy local)
- Content type: `application/json`
- Secret: `GITHUB_WEBHOOK_SECRET` (giống với biến môi trường bạn cấu hình)
- Chọn events: `Push` và/hoặc `Release` hoặc `Let me select individual events`.

## Script updater
- `updater\updater.ps1` nhận 3 tham số: `<repoPath> [serviceName] [restartCmd]`.
- Mặc định server truyền dòng `repoPath` và `serviceName` từ biến môi trường. Bạn có thể chỉnh thay đổi để phù hợp môi trường.

## Test
- Có một unit test mẫu `tests/test_signature.py` (cần chạy `pytest`).

## Tiếp theo
- (Tùy chọn) Triển khai server public hoặc dùng ngrok để kiểm thử webhook từ GitHub.
- Thêm logging/monitoring, rollback strategy, và kiểm tra quyền truy cập file khi cập nhật.
