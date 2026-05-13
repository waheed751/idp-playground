import os, requests
from dotenv import load_dotenv
from aws_requests_auth.aws_auth import AWSRequestsAuth

load_dotenv(dotenv_path=".env")

auth = AWSRequestsAuth(
    aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_host="pksbevjmgg.execute-api.us-east-1.amazonaws.com",
    aws_region=os.getenv("AWS_REGION", "us-east-1"),
    aws_service="execute-api",
)

response = requests.post(
    "https://pksbevjmgg.execute-api.us-east-1.amazonaws.com/dev/ocr",
    json={
        "file": "s3://doclus.ai-demos/insurance/COI_&_EPI_exp._9-1-18_20260512_112433.pdf",
        "type": "Insurance",
        "structure": {}
    },
    auth=auth,
    timeout=30
)

print("Status:", response.status_code)
print("Full response:", response.json())
