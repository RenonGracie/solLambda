import boto3

__s3_client = boto3.client('s3')

S3_BUCKET_NAME = "therapists-personal-data"

def get_video_url(object_name, expiration=3600):
    return __s3_client.generate_presigned_url('get_object',
                                                  Params={'Bucket': S3_BUCKET_NAME,
                                                          'Key': f"videos/{object_name}"},
                                                  ExpiresIn=expiration)