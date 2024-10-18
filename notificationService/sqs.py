import boto3
import asyncio
import json

class SQSManager:
    def __init__(self, queue_url: str):
        self.sqs = boto3.client('sqs', region_name='ap-south-1')
        self.queue_url = queue_url

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