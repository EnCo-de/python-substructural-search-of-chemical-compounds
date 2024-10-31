import os
import boto3  # import boto3.session
from botocore.exceptions import ClientError

def main(instance_id: str):
    """
    Replaces the code associated with a running instance. The
    instance is rebooted to ensure that it uses the new commit.
    When the instance is ready, Docker compose is used
    to restart the Python web server.

    :param instance_id: The ID of the instance to restart.
    """

    # Initialize a session using AWS credentials
    session = boto3.Session(
        aws_access_key_id=os.getenv('ACCESS_KEY'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    ec2_client = session.client('ec2', region_name='us-east-1')

    ec2_client.reboot_instances(InstanceIds=[instance_id])
    print("Rebooting instance %s." % instance_id)
    waiter = ec2_client.get_waiter("instance_running")
    print("Waiting for instance to be running.")
    waiter.wait(InstanceIds=[instance_id])
    print("Instance is now running.")

if __name__ == '__main__':
    main(os.getenv('NEW_EC2_INSTANCE'))
