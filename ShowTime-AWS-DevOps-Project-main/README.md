# ShowTime – AWS Movie Ticket Booking Application

A cloud-based movie ticket booking application built using Python, Flask, and AWS services.

## Project Overview

ShowTime is a movie ticket booking web application with customer and administrator functionality. It uses AWS services for cloud-based data storage and notifications.

## Features

- Customer registration and login
- Administrator login and dashboard
- Movie management (add and delete movies)
- Movie ticket booking functionality
- Customer and admin notifications
- AWS DynamoDB integration

## Technology Stack

| Category | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | AWS DynamoDB |
| Notifications | AWS SNS |
| Email | AWS SES |
| Cloud Platform | AWS |
| Version Control | Git, GitHub |

## AWS Services

- Amazon DynamoDB – Application data storage
- Amazon SNS – Notification delivery
- Amazon SES – Email communication
- Amazon EC2 – Planned application deployment

## Project Documentation

Detailed project documentation is available in the following files:

- `MayankShowTimeProject.pdf` – Main application documentation.
- `aws console imp command.pdf` – AWS commands, execution sequence, and console setup instructions.

## Local Setup

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ShowTImeAwsProject
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your AWS credentials and required environment variables securely before running the application.

Start the application:

```bash
python app.py
```

## Future DevOps Enhancements

- GitHub Actions CI/CD
- Docker containerization
- Amazon ECR integration
- AWS EC2 deployment
- CloudWatch monitoring
- Terraform infrastructure automation

## Project Status

Application development and initial AWS integration completed. DevOps automation and deployment enhancements are in progress.
