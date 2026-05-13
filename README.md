# OCR Playground

A Streamlit demo app for extracting structured data from Insurance PDFs using your AWS OCR API.

## Project Structure

```
ocr_playground/
├── app.py                  # Entry point — login / register
├── pages/
│   └── playground.py       # Main OCR playground page
├── utils/
│   ├── db.py               # PostgreSQL connection + user auth
│   └── ocr_api.py          # POST job, poll, GET result
├── requirements.txt
└── .env.example
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ocr_playground
DB_USER=postgres
DB_PASSWORD=yourpassword

OCR_API_BASE=https://pksbevjmgg.execute-api.us-east-1.amazonaws.com/dev/ocr
```

### 3. Create the PostgreSQL database

```sql
CREATE DATABASE ocr_playground;
```

The `users` table is created automatically on first run.  
A default user `admin` / `admin123` is also created automatically.

### 4. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501

## How it works

1. User logs in (or registers) via the login page
2. On the playground page, paste an S3 path like:
   `s3://sudobricks-temp/ocr/your-file.pdf`
3. Click **Run OCR** — the app:
   - POSTs to `/dev/ocr` with the file path + Insurance structure
   - Polls the GET endpoint every 3 seconds until `status == fulfilled`
   - Displays the extracted data in structured cards
4. You can also manually fetch any past job by entering its UUID

## Default credentials (demo)

| Username | Password |
|----------|----------|
| admin    | admin123 |

## Adding new users

Register from the UI, or insert directly into PostgreSQL:

```sql
INSERT INTO users (username, password, full_name)
VALUES ('newuser', 'password123', 'New User');
```
