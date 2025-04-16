# OptionsWizard Google Cloud Deployment Guide

This document provides instructions for deploying the OptionsWizard Discord bot and Streamlit admin interface to Google Cloud Platform.

## Prerequisites

1. Google Cloud Platform account
2. Basic familiarity with Google Cloud console
3. Discord Bot Token
4. Polygon.io API Key

## Method 1: Deploy using Google Cloud Run (Recommended)

Google Cloud Run is a fully managed platform that automatically scales your containerized applications.

### Step 1: Install Google Cloud SDK

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) on your local machine
2. Initialize the SDK: `gcloud init`
3. Authenticate: `gcloud auth login`

### Step 2: Set Up Google Cloud Project

1. Create a new Google Cloud project or select an existing one:
   ```
   gcloud projects create [PROJECT_ID] --name="OptionsWizard"
   ```
   or
   ```
   gcloud config set project [PROJECT_ID]
   ```

2. Enable required APIs:
   ```
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
   ```

### Step 3: Prepare the Application for Deployment

1. Download your project from Replit
2. Create a `Dockerfile` in your project root:

```Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create environment file
RUN echo "DISCORD_TOKEN=${DISCORD_TOKEN}" > .env
RUN echo "POLYGON_API_KEY=${POLYGON_API_KEY}" >> .env

# Command to run on container start
CMD ["python", "main.py"]
```

3. Create a `requirements.txt` file with your dependencies:

```
discord.py
matplotlib
numpy
pandas
python-dateutil
python-dotenv
pytz
requests
scipy
streamlit
trafilatura
yfinance
```

### Step 4: Build and Deploy the Container

1. Build the container image:
   ```
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/options-wizard
   ```

2. Deploy to Cloud Run:
   ```
   gcloud run deploy options-wizard \
     --image gcr.io/[PROJECT_ID]/options-wizard \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars="DISCORD_TOKEN=your_discord_token,POLYGON_API_KEY=your_polygon_api_key"
   ```

3. Google Cloud Run will provide you with a URL where your application is hosted

### Step 5: Set Up Continuous Running

Since Discord bots need to run continuously:

1. Configure the minimum instances to 1 to ensure the bot is always running:
   ```
   gcloud run services update options-wizard \
     --min-instances=1
   ```

## Method 2: Using Google Compute Engine VM

For more control over the environment, you can use a Google Compute Engine VM.

### Step 1: Create a VM Instance

1. Go to Google Cloud Console > Compute Engine > VM instances
2. Click "Create Instance"
3. Configure your instance:
   - Name: options-wizard
   - Machine type: e2-micro (for cost efficiency)
   - Boot disk: Ubuntu 20.04 LTS
   - Allow HTTP/HTTPS traffic
4. Click "Create"

### Step 2: Connect to the VM and Set Up the Environment

1. Connect to your VM via SSH from the Google Cloud Console
2. Update and install dependencies:
   ```
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv git
   ```

3. Clone your code or upload it to the VM
   ```
   git clone https://github.com/yourusername/options-wizard.git
   cd options-wizard
   ```

4. Set up Python environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Create `.env` file with your secrets:
   ```
   echo "DISCORD_TOKEN=your_discord_token" > .env
   echo "POLYGON_API_KEY=your_polygon_api_key" >> .env
   ```

### Step 3: Run the Application as a Background Service

1. Create a systemd service file:
   ```
   sudo nano /etc/systemd/system/options-wizard.service
   ```

2. Add the following content:
   ```
   [Unit]
   Description=OptionsWizard Discord Bot
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/home/<your-username>/options-wizard
   ExecStart=/home/<your-username>/options-wizard/venv/bin/python main.py
   Restart=always
   RestartSec=10
   Environment=PATH=/home/<your-username>/options-wizard/venv/bin:$PATH

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```
   sudo systemctl enable options-wizard
   sudo systemctl start options-wizard
   ```

4. Check the status:
   ```
   sudo systemctl status options-wizard
   ```

## Method 3: Using Google App Engine (Another Option)

Google App Engine is a platform for building scalable web applications and backend services.

### Step 1: Prepare your application

1. Create an `app.yaml` file in your project root:
   ```yaml
   runtime: python311

   entrypoint: python main.py

   env_variables:
     DISCORD_TOKEN: YOUR_DISCORD_TOKEN
     POLYGON_API_KEY: YOUR_POLYGON_API_KEY
   ```

2. For long-running applications, specify manual scaling:
   ```yaml
   manual_scaling:
     instances: 1
   ```

### Step 2: Deploy to App Engine

1. Install the Google Cloud SDK if you haven't already
2. Deploy your application:
   ```
   gcloud app deploy
   ```

## Monitoring and Maintenance

### Set Up Monitoring

1. Set up Google Cloud Monitoring to track your application's performance and uptime
2. Create alerts for critical events

### Set Up Regular Backups

For the VM approach, set up regular backups of your data:
```
# Create a snapshot schedule for your VM disk
gcloud compute resource-policies create snapshot-schedule options-wizard-backup \
  --description="OptionsWizard weekly backup" \
  --start-time=04:00 \
  --daily-schedule \
  --storage-location=us-central1
```

## Additional Tips

1. **Use Secret Manager**: Instead of hardcoding secrets in environment variables, use Google Secret Manager:
   ```
   # Store secrets
   gcloud secrets create discord-token --replication-policy="automatic"
   echo -n "your-discord-token" | gcloud secrets versions add discord-token --data-file=-
   ```

2. **Use a Custom Domain**: If you're using the Streamlit admin interface, you might want to set up a custom domain

3. **Set Up Logging**: Configure comprehensive logging to troubleshoot issues:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                      handlers=[logging.FileHandler("bot.log"),
                                logging.StreamHandler()])
   ```

4. **Implement Health Checks**: Add a health check endpoint to your application to monitor its status

5. **Set Up Auto-Scaling** (for Cloud Run): Configure auto-scaling based on CPU usage or request volume