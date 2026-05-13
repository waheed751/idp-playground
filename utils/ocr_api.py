import os
import time
import requests
from dotenv import load_dotenv
from aws_requests_auth.aws_auth import AWSRequestsAuth

load_dotenv()

BASE_URL = os.getenv(
    "OCR_API_BASE",
    "https://pksbevjmgg.execute-api.us-east-1.amazonaws.com/dev/ocr"
)
_host = BASE_URL.replace("https://", "").replace("http://", "").split("/")[0]
_region = os.getenv("AWS_REGION", "us-east-1")


def _get_auth():
    return AWSRequestsAuth(
        aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_host=_host,
        aws_region=_region,
        aws_service="execute-api",
    )


def submit_ocr_job(s3_path: str, api_type: str, structure: dict) -> dict:
    """POST to OCR endpoint. api_type is exactly what the API expects."""
    payload = {
        "file": s3_path,
        "type": api_type,
        "structure": structure
    }
    response = requests.post(BASE_URL, json=payload, auth=_get_auth(), timeout=30)
    response.raise_for_status()
    return response.json()


def get_job_result(job_id: str) -> dict:
    url = f"{BASE_URL}/{job_id}"
    response = requests.get(url, auth=_get_auth(), timeout=30)
    response.raise_for_status()
    return response.json()


def poll_until_done(job_id: str, max_wait: int = 120, interval: int = 3) -> dict:
    elapsed = 0
    while elapsed < max_wait:
        result = get_job_result(job_id)
        status = result.get("status", "")
        if status == "fulfilled":
            return result
        if status == "failed":
            raise Exception(f"job failed: {result.get('error_message', 'Unknown error')}")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError(f"job did not complete within {max_wait} seconds.")
