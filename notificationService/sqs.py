import boto3
import asyncio
import json

from config import settings

class SQSManager:
    def __init__(self):
        self.sqs = boto3.client('sqs', region_name='ap-south-1', aws_access_key_id=settings.AWS_ACCESS_KEY, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        queue_url_response = self.sqs.get_queue_url(QueueName = settings.SQS_QUEUE_NAME)
        self.queue_url = queue_url_response["QueueUrl"]

    async def receive_messages(self, broadcast_function):
        """Function to poll messages from SQS and broadcast them."""
        print(f"Waiting for messages from {self.queue_url}. To exit press CTRL+C...")
        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=10
                )

                messages = response.get('Messages', [])
                for message in messages:
                    # Parse the message body
                    notification = json.loads(message['Body'])
                    user_id = notification.get("user_id")
                    user_type = notification.get("user_type")
                    status = notification.get("status", "success")
                    message_body = notification.get("message")
                    params = notification.get("params", {})

                    # Broadcast the message to the specified user
                    await broadcast_function(message_body, user_id, user_type, status, params)

                    # Delete the message from SQS after processing
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )

                await asyncio.sleep(1)
            except Exception as e:
                print("Error consuming messages from SQS: ", str(e))
                await asyncio.sleep(5)