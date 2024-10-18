import datetime
import pytz
import boto3
import json
from sqlalchemy import text
from app.config import settings


sqs = boto3.client("sqs", region_name="ap-south-1")
notification_queue_url = settings.SQS_NOTIFICATION_QUEUE_URL

def get_current_time():
    return datetime.datetime.now(pytz.timezone("Asia/Kolkata"))


def convert_ll_to_point(latitude: float, longitude: float):
    point = f'POINT({longitude} {latitude})'
    return text(f"ST_GeomFromText('{point}', 4326)")


def convert_point_to_ll(point):
    longitude, latitude = map(float, point.strip('POINT()').split())
    return {"latitude": latitude, "longitude": longitude}


def publish_to_sqs(message: dict):
    response = sqs.send_message(
        QueueUrl=notification_queue_url,
        MessageBody=json.dumps(message)
    )
    return response