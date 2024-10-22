import boto3
import asyncio
from app.routes.booking import create_new_booking
from app.config import settings


# Initialize SQS client
sqs = boto3.client('sqs', region_name='ap-south-1', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
queue_url_response = sqs.get_queue_url(QueueName = settings.SQS_QUEUE_URL)
QUEUE_URL = queue_url_response["QueueUrl"]


async def consume_sqs_messages():
    """
    Poll SQS for messages and process them asynchronously.
    """
    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=10,  # Fetch up to 10 messages at once
            WaitTimeSeconds=10
        )

        if "Messages" in response:
            tasks = [create_new_booking(msg) for msg in response["Messages"]]
            await asyncio.gather(*tasks)

            # Delete processed messages from the queue
            for msg in response["Messages"]:
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=msg["ReceiptHandle"])