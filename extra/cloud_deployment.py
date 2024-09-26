import os
import boto3  # import boto3.session
from botocore.exceptions import ClientError

def main():
    # Initialize a session using AWS credentials
    session = boto3.Session(
        aws_access_key_id=os.getenv('ACCESS_KEY'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
        region_name='us-east-1'
    )
    ec2_client = session.client('ec2', region_name='us-east-1')

    response = ec2_client.reboot_instances(
        InstanceIds=[os.getenv('NEW_EC2_INSTANCE')]
    )
    print('... World!')
    return response

if __name__ == '__main__':
    print('CI/CD Continuous Integration, Continuous Delivery')