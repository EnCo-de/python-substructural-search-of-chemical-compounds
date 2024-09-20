# Homework 11

# AWS
 
## Part 1. Base HomeWork
1. Adopt your GitHub workflow to have your application running in the cloud - your workflow should implement ssh session to the instance, install all required software if needed and run your application.
 
Some hints:
* store your IAM User credentials as a secrets in your GitHub repo
* use specific GitHub Actions to managed to have AWS access for your IAM User
* for ssh session to may use this simple action -
https://github.com/appleboy/ssh-action
* Think about how to upload your code inside your EC2 instance (simple scp, from S3 by using awscli etc.) and implement it. It's up to you.
 
Describe in your style how you implemented deployment of your application inside a Readme file in your GitHub repo. 
And of course we will look on your workflow file in _.github_ directory. :)
 
## Part 2. Lambda & Boto3
 
> Prerequisites:
> * Install Python (3.x).
> * Install the AWS SDK for Python (Boto3) using pip
> * Configure your AWS CLI with your credentials
 
1. Create a Simple Lambda Function. In your AWS Management Console, navigate to the Lambda service.
* Create a new Lambda function.
* Choose "Author from scratch."
* Name your function (e.g., `HelloStudentFunction`).
* Select Python 3.x as the runtime.
* Use the following code for your Lambda function:
 
>     def lambda_handler(event, context):
>         name = event.get('name', 'World')
>         return {
>                'statusCode': 200,
>                'body': f'Hello, {name}!'
>         }
 
2. Test Your Lambda Function. In the AWS Lambda console, create a test event:
* Name your event (e.g., `TestEvent`).
* Use the following JSON:
 
>     {
>     "name": "Student" 
>     }
Run the test and check the output.
 
3. Deploy and Invoke the Function Using Boto3.
Create a new Python file called `invoke_lambda.py`.
What you need to have inside that file:
* Initialize a session using your AWS credentials
* Define the event you want to send
* Invoke the Lambda function
* Read the response
 
4. Run Your Invocation Script. 
* Execute `invoke_lambda.py` to see the output from your Lambda function.
* You should see a response similar to:
 
>     {
>     "statusCode": 200,
>     "body": "Hello, Alice!" 
>     }
 
5. Bonus Challenge (Optional):
 
* Extend the Lambda function to accept a list of names and return greetings for each name.
* Modify your invocation script to test this new functionality.
 
As a result, upload your `invoke_lambda.py` to your repo.
 
## Part 3. Extra HomeWork (ECS) (Optional)
1. Deploy simple [nginx demo application](
https://hub.docker.com/r/nginxdemos/hello/)
in ECS (EC2 type of launch). 
* Don't forget to use Free Tier Eligible _t2.micro_ instance.
 
As a result, upload 2 screenshots:
a) With instance's metadata from nginx page (we will look on DNS name), 
b) With the same DNS name of your instance from EC2 page in AWS console.
2. (Optionally) Manage to upload image from your public ECR.
 
3. And don't forget to terminate all resources that may cause spendings.
## Part 4. Extra HomeWork (K8S) (Optional)
Prerequisites:
 
> *  Install Minikube on your local machine. Follow the [Minikube installation guide](
https://minikube.sigs.k8s.io/docs/start/?arch=/macos/arm64/stable/binary%20download).
> *  Install kubectl, the Kubernetes command-line tool. Follow the [kubectl installation guide](
https://kubernetes.io/docs/tasks/tools/#kubectl).
> *  Ensure you have Docker installed :)
 

Deploy your application in minikube on your local machine.
* Create and apply all yaml manifests for all component of your application. 
* Manage to connect those components according to the logic of application. 
As a result, upload your manifests(app components, services etc) to your repo.
 
Well done! Can't wait to see your results!