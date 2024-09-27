# CI/CD Continuous Integration, Continuous Delivery
_Describes how deployment of this application is implemented from its GitHub repo_

1. [GitHub workflow to have your application running in the cloud](#github-workflow-to-have-your-application-running-in-the-cloud)
2. [Connecting to your Linux instance using an SSH client](#1-connecting-to-your-linux-instance-using-an-ssh-client)
3. [Installing required software](#2-installing-required-software)
4. [User data shell scripts](#3-user-data-shell-scripts)


## GitHub workflow to have your application running in the cloud
_Keeping the workflow implementation as simple as possible._

> cloud_deployment.yml

### Running your workflow when a pull request merges
> When a pull request merges, the pull request is automatically closed. 

The following _Python cloud deployment_ workflow is triggered and will run whenever a pull request to _deploy_ branch closes. The implement_deployment job will only run if the pull request was also merged.

Replaces the code associated with a running instance. The instance is rebooted to ensure that it uses the newly pushed commit.
When the instance is ready, Docker compose is used to restart the Python web server.

1. Store your credentials, tokens, SSH keys as secrets in your GitHub repo
2. Install the AWS SDK for Python (Boto3) using pip.
3. Invoke extra\cloud_deployment.py Python script that
    - Initializes a session using your AWS credentials.
    - Requests a reboot of the specified instances programmatically.

Allow enough time for the instance to launch and run the directives in your user data, and then check to see that your directives have completed the tasks you intended.

For example, in a web browser, enter the test URL. This URL is the public DNS address of your instance followed by a forward slash.

http://your.public.dns.amazonaws.com/

## 1. Connecting to your Linux instance using an SSH client
- To run the commands remotely, connect to your Linux virtual private server (VPS) using Secure Shell (SSH). [Use the following procedure][ssh].

## 2. Installing required software
- To get started, install Docker and Docker Compose tool for defining and running multi-container applications on Ubuntu, by following the [Docker Engine installation steps][dock].
- On Debian and Ubuntu, the Docker service starts on boot by default.
- Unlike the two command utilities, extracting files similar to other compression formats, such as tar and gzip, unzip is not installed by default. Thus, install and use _unzip_ to extract .zip files on a Linux VPS.
- For Debian-based operating systems like Ubuntu, use the APT package manager to install _unzip_ in Linux. Before doing so, update and upgrade the repository with the following commands:
    ```sh
    sudo apt update && sudo apt upgrade
    ```
    Then, install unzip using this:
    ```sh
    sudo apt install unzip
    ```

## 3. User data shell scripts
- This new user data will replace the current user data connected with this instance
    ```bash
    #!/bin/bash
    cd ~
    wget https://github.com/EnCo-de/python-substructural-search-of-chemical-compounds/archive/refs/heads/deploy.zip
    unzip deploy.zip
    cd python-substructural-search-of-chemical-compounds-deploy
    docker compose -p subs up -d
    ```

    > GNU wget is a free utility for non-interactive download of files from the Web. It supports the most widely used HTTP, HTTPS, and FTP Internet protocols. It is a non-interactive commandline tool, so it may easily be called from scripts. _wget_ function retrieves one or more files and saves them to a local directory.
- User data shell script will upload [the latest code pushed to _deploy_ branch on GitHub][code] inside your Linux instance, extract it, build and cobine multiple services in Docker containers.
    > User data and shell scripting is the easiest and most complete way to send instructions to an instance at launch. By default, user data scripts run only during the boot cycle when you first launch an instance.

- You can update your configuration to ensure that your user data scripts run every time you restart your instance. Scripts entered as user data are run as the root user, so do not use the _sudo_ command in the script.


   [ssh]: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/connect-linux-inst-ssh.html>
   [dock]: <https://docs.docker.com/engine/install/ubuntu/>
   [code]: <https://github.com/EnCo-de/python-substructural-search-of-chemical-compounds/tree/deploy>
   