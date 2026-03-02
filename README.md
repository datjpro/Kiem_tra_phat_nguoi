# Kiem tra phat nguoi Telegram Bot

He thong bot Telegram kiem tra phat nguoi cho:
- Xe may (`xemay`)
- O to (`oto`)

Bot ho tro:
- Kiem tra ngay theo bien so (`/check`)
- Theo doi dinh ky va thong bao khi co thay doi (`/track`, `/untrack`, `/list`)

## 1) Cai dat

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2) Cau hinh

Sao chep file mau:

```bash
copy .env.example .env
```

Cap nhat `.env`:

```env
TELEGRAM_BOT_TOKEN=<token tu BotFather>
PROVIDER_MODE=mock
POLL_INTERVAL_SECONDS=600
SQLITE_PATH=data/bot.db
```

### Che do provider

- `PROVIDER_MODE=mock`: Demo nhanh, khong can API ben ngoai.
- `PROVIDER_MODE=http`: Goi API ben ngoai theo contract ben duoi.

Neu dung `http`, can them:

```env
HTTP_PROVIDER_URL=https://your-provider-domain
HTTP_PROVIDER_TOKEN=<optional>
REQUEST_TIMEOUT_SECONDS=20
```

## 3) Chay bot

```bash
python -m src.main
```

## 4) Lenh Telegram

- `/start`
- `/help`
- `/check <bien_so> <oto|xemay>`
  - Vi du: `/check 30A-12345 oto`
- `/track <bien_so> <oto|xemay>`
- `/untrack <bien_so> <oto|xemay>`
- `/list`

## 5) HTTP Provider Contract

Bot se goi:

- `POST {HTTP_PROVIDER_URL}/check`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <HTTP_PROVIDER_TOKEN>` (neu co)
- Body:

```json
{
  "plate": "30A12345",
  "vehicle_type": "oto"
}
```

Response:

```json
{
  "violations": [
    {
      "id": "VP-001",
      "date": "2026-01-18 10:45",
      "location": "Nguyen Trai, Ha Noi",
      "behavior": "Vuot den do",
      "fine": "4.000.000 - 6.000.000 VND",
      "source": "provider-name"
    }
  ]
}
```

Neu khong co vi pham:

```json
{
  "violations": []
}
```

## 6) Luu y thuc te

- Nhieu nguon phat nguoi cong khai co CAPTCHA/chong bot, ban nen dung API hop phap (noi bo hoac ben thu 3) thay vi scrape truc tiep.
- Du lieu xu ly theo moi chat Telegram: moi nguoi dung tu theo doi danh sach rieng.
