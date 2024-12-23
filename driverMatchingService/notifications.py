import boto3
import json

from config import settings


sqs_client = boto3.client('sqs', region_name='ap-south-1', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
queue_url_response = sqs_client.get_queue_url(QueueName = settings.SQS_NOTIFICATION_QUEUE_URL)
SQS_QUEUE_URL = queue_url_response["QueueUrl"]

async def notify_driver(driver_id, customer_details):
    """Send notification to SQS."""
    try:
        message = {
            "user_id": driver_id,
            "user_type": "driver",
            "status": "trip_request",
            "message_body": "New trip request from Customer.",
            "params": customer_details
        }

        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message),
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"Notified Driver {driver_id} for Trip.")
        else:
            print(f"Failed to notify Driver {driver_id}.")
    except Exception as e:
        raise e