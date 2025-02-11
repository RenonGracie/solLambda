import boto3
from botocore.exceptions import ClientError

from src.models.api.therapist_s3 import S3MediaType
from src.utils.settings import settings

_s3_client = boto3.client("s3")

S3_BUCKET_NAME = "therapists-personal-data"


def get_media_url(user_id: str, s3_media_type: S3MediaType, expiration=3600):
    if settings.IS_AWS is False:
        return None

    match s3_media_type:
        case S3MediaType.IMAGE:
            link = f"images/{user_id}"
        case S3MediaType.WELCOME_VIDEO:
            link = f"videos/{user_id}_welcome"
        case S3MediaType.INTRO_VIDEO:
            link = f"videos/{user_id}_intro"
        case _:
            return None

    try:
        _s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=link)
        return _s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": link},
            ExpiresIn=expiration,
        )
    except ClientError:
        return None
