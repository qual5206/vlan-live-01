import time
import json
import docker
import boto3

sqs = boto3.client('sqs')
asg = boto3.client('autoscaling')
docker_client = docker.from_env()

queue_url = 'https://sqs.us-west-2.amazonaws.com/456410706824/valheim-default-lifecycle'
# frustrating to hard code this, idk about this quite yet
while True:
    try:
        print('Trying to receive.')
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp',
                'SequenceNumber'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=5,
            WaitTimeSeconds=2
        )

        message = response['Messages'][0]
        message_body = json.loads(message['Body'])

        receipt_handle = message['ReceiptHandle']
        metadata = json.loads(message_body['NotificationMetadata'])

        lifecycle_hook_name = message_body['LifecycleHookName']
        autoscaling_group_name = metadata['asgName']

        # Delete the message once I receive
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        # docker shutdown then wait 10s
        containers = docker_client.containers.list()
        containers[0].stop()

        # wait for init_script to back up the world as it is after the stop
        time.sleep(30)

        # now you can allow the instance to die
        response = asg.complete_lifecycle_action(
            LifecycleHookName=lifecycle_hook_name,
            AutoScalingGroupName=autoscaling_group_name,
            LifecycleActionResult='COMPLETE',
            LifecycleActionToken=message['LifecycleActionToken']
        )
        # ur gonna die anyway LUL
        break
    except KeyError as e:
        print('KeyError, potentially expected. :: {}'.format(e))
