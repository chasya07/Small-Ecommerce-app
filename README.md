🛒 Ecommerce Project: Automated CI/CD Pipeline for Flask eCommerce App on AWS

📑 Table of Contents

Project Overview
Architecture Diagram
Step 1: AWS EC2 Instance Preparation
Step 2: Install Dependencies on EC2
Step 3: Jenkins Installation and Setup
Step 4: GitHub Repository Configuration
Dockerfile
docker-compose.yml
Jenkinsfile
Step 5: Jenkins Pipeline Creation and Execution
Conclusion

1. Project Overview

This document outlines the step-by-step process for deploying a containerized Flask-based eCommerce application (Flask + SQLite) on an AWS EC2 instance. The deployment is containerized using Docker and Docker Compose. A full CI/CD pipeline is established using Jenkins to automate the build and deployment process whenever new code is pushed to a GitHub repository.

2. Architecture Diagram

+-----------------+      +----------------------+      +-----------------------------+
|   Developer     |----->|     GitHub Repo      |----->|  Jenkins Server             |
| (pushes code)   |      | (Source Code Mgmt)   |      |  (Running on AWS EC2)       |
+-----------------+      +----------------------+      |                             |
                                                       | 1. Clones Repo              |
                                                       | 2. Builds Docker Image      |
                                                       | 3. Runs Docker Compose      |
                                                       +--------------+--------------+
                                                                      |
                                                                      | Deploys
                                                                      v
                                                       +-----------------------------+
                                                       |      Application Server     |
                                                       |      (Running on AWS EC2)   |
                                                       |                             |
                                                       | +-------------------------+ |
                                                       | | Docker Container: Flask | |
                                                       | +-------------------------+ |
                                                       |              |              |
                                                       |              v              |
                                                       | +-------------------------+ |
                                                       |       Gunicorn Server       |
                                                       |       SQLite (store.db)     |
                                                       | +-------------------------+ |
                                                       +-----------------------------+
3. Step 1: AWS EC2 Instance Preparation

1.Launch EC2 Instance:
  Navigate to the AWS EC2 console.
  Launch a new instance using the Amazon Linux 2023 (kernel-6.1) AMI.
  Select the c7i-flex.large instance type for free-tier eligibility.
  Create and assign a new key pair for SSH access.



2.Configure Security Group:
  Create a security group with the following inbound rules:
  Type: SSH, Protocol: TCP, Port: 22, Source: Your IP
  Type: HTTP, Protocol: TCP, Port: 80, Source: Anywhere (0.0.0.0/0)
  Type: Custom TCP, Protocol: TCP, Port: 5000 (for Flask), Source: Anywhere (0.0.0.0/0)
  Type: Custom TCP, Protocol: TCP, Port: 8080 (for Jenkins), Source: Anywhere (0.0.0.0/0)


3.Connect to EC2 Instance:
  Use SSH to connect to the instance's public IP address.
  ssh -i /path/to/key.pem ec2-user@<ec2-public-dns>
  
4. Step 2: Install Dependencies on EC2

   1.Install Git, Docker, and Docker Compose:
     --> yum install git docker -y
     --> install compose by using below commands
         sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
         sudo chmod +x /usr/local/bin/docker-compose
         sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
         sudo yum install -y python3-pip
         sudo pip3 install docker-compose
     
   2.Start and Enable Docker:
     sudo systemctl start docker
     sudo systemctl enable docker

5. Step 3: Jenkins Installation and Setup

   1.Install Java: 
     yum install java-17-amazon-corretto -y

   2.Add Jenkins Repository and Install:
     sudo wget -O /etc/yum.repos.d/jenkins.repo \
     https://pkg.jenkins.io/rpm-stable/jenkins.repo
     yum install jenkins -y 

   3.Start and Enable Jenkins Service:
     systemctl start jenkins
     systemctl enable jenkins

   4.Initial Jenkins Setup:
     Retrieve the initial admin password:
     cat /var/lib/jenkins/secrets/initialAdminPassword
     Access the Jenkins dashboard at http://<ec2-public-ip>:8080.
     Paste the password, install suggested plugins, and create an admin user.

   5.Grant Jenkins Docker Permissions:
     sudo usermod -aG docker jenkins
     sudo systemctl restart jenkins

6. Step 4: GitHub Repository Configuration

   Ensure your GitHub repository contains the following three files.

   Dockerfile

   This file defines the environment for the Flask application container.

   # Use an official Python runtime as a parent image
   FROM python:3.11-slim

   # Set the working directory in the container
   WORKDIR /app

   # Copy the requirements file to leverage Docker cache
   COPY requirements.txt .

   # Install Python dependencies
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy the rest of the application code
   COPY . .

   # Expose the port the app runs on
   EXPOSE 5000

   # Command to run the application
   CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

   docker-compose.yml

   version: "3.8"

   services:
     flask-app:
       build: .
       container_name: ecommerce-app
       ports:
         - "5000:5000"
       volumes:
         - sqlite-data:/app
       restart: always

   volumes:
     sqlite-data:
   
   Jenkins File
   
   This file contains the pipeline-as-code definition for Jenkins.
   pipeline {
    agent any
    stages {
        stage('Code') {
            steps {
                git branch: 'ecommerce', url: 'https://github.com/chasya07/projects.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t ecommerce-app:latest .'
            }
        }
        stage('Deploy Application') {
            steps {
                sh 'docker-compose down || true'
                sh 'docker compose up -d --build'
            }
        }
     }
   }

7. Step 5: Jenkins Pipeline Creation and Execution

   Create a New Pipeline Job in Jenkins:

   From the Jenkins dashboard, select New Item.
   Name the project, choose Pipeline, and click OK.
   Configure the Pipeline:

   In the project configuration, scroll to the Pipeline section.
   Set Definition to Pipeline script from SCM.
   Choose Git as the SCM.
   Enter your GitHub repository URL.
   Verify the Script Path is Jenkinsfile.
   Save the configuration.


   Run the Pipeline:
   Click Build Now to trigger the pipeline manually for the first time.
   Monitor the execution through the Stage View or Console Output.




   Verify Deployment:
   After a successful build, your Flask application will be accessible at http://<your-ec2-public-ip>:5000.
   Confirm the containers are running on the EC2 instance with docker ps.
8. Conclusion

   The CI/CD pipeline is now fully operational. Any git push to the main branch of the configured GitHub repository will automatically trigger the Jenkins pipeline, which will build the new Docker image
   and deploy the updated application, ensuring a seamless and automated workflow from development to production.


