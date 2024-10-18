import boto3
import asyncio
from app.routes.booking import create_new_booking
from app.config import settings


# Initialize SQS client
sqs = boto3.client("sqs", region_name="ap-south-1")
QUEUE_URL = settings.SQS_QUEUE_URL


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