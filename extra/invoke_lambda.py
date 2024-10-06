import os
import json
import boto3  # import boto3.session
from botocore.exceptions import ClientError

# Initialize a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=os.getenv('ACCESS_KEY'),
    aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)
lambda_client = session.client('lambda', region_name='us-east-1')


def invoke_function(function_name, function_params, get_log=False):
    """
    Invokes a Lambda function.

    :param function_name: The name of the function to invoke.
    :param function_params: The parameters of the function as a dict. This dict
                            is serialized to JSON before it is sent to Lambda.
    :param get_log: When true, the last 4 KB of the execution log are included in
                    the response.
    :return: The response from the function invocation.
    """
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(function_params),
            InvocationType='RequestResponse',
            LogType="Tail" if get_log else "None",
        )
        print("Invoked function %s (%s)." % (function_name, function_params.get('name', '')))
        # Read the response
        load = response.get('Payload')
        j = json.loads(load.read()) if load else None
        print(json.dumps(j, indent=4))
    except ClientError:
        print("Couldn't invoke function %s." % function_name)
        raise
    return j  # response


# Define the events you want to send
event = (
    {},
    {'name': 'Joe'}
    )
# Invoke the Lambda function
response = invoke_function('HelloStudentFunction', event[0])
response = invoke_function('HelloStudentFunction', event[1])

# Invoked function HelloStudentFunction ().
# {
#     "statusCode": 200,
#     "body": "Hello from Lambda, World!"
# }

# Invoked function HelloStudentFunction (Joe).
# {
#     "statusCode": 200,
#     "body": "Hello from Lambda, Joe!"
# }