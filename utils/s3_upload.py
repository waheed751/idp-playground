import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv()

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'doclus.ai-demos')


def _get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'us-east-1')
    )


def make_timestamped_filename(original_filename: str) -> str:
    """my doc.pdf → my_doc_20260512_143022.pdf"""
    name, ext = os.path.splitext(original_filename)
    name_clean = name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name_clean}_{timestamp}{ext}"


def upload_fileobj_to_s3(file_obj, original_filename: str, s3_folder: str) -> dict:
    """
    Upload file to S3 under the correct folder based on doc type.
    s3_folder: 'insurance', 'rentroll', or 'pfs'
    Returns dict with s3_uri, filename, success, error.
    """
    timestamped_name = make_timestamped_filename(original_filename)
    s3_key = f"{s3_folder}/{timestamped_name}"

    try:
        _get_s3_client().upload_fileobj(
            file_obj,
            BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": "application/pdf"}
        )

        return {
            "success": True,
            "s3_uri": f"s3://{BUCKET_NAME}/{s3_key}",
            "s3_key": s3_key,
            "file_url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}",
            "filename": timestamped_name,
        }

    except FileNotFoundError:
        return {"success": False, "error": "File not found."}
    except NoCredentialsError:
        return {"success": False, "error": "S3 credentials missing. Check S3_ACCESS_KEY_ID in .env"}
    except ClientError as e:
        return {"success": False, "error": e.response['Error']['Message']}
