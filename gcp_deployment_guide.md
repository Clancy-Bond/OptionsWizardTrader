# OptionsWizard Deployment Guide for a 10,000-User Discord Server

This simplified guide will walk you through deploying your Discord bot to Google Cloud Platform, with instructions for both Compute Engine and Cloud Run approaches.

## Option 1: Google Compute Engine (Recommended for Simplicity)

### Step 1: Create Your VM

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select your existing project
3. Navigate to "Compute Engine" → "VM Instances" → "Create Instance"
4. Fill in these settings:
   - **Name**: options-wizard
   - **Region**: Choose one close to most of your users
   - **Machine type**: e2-standard-2 (2 vCPUs, 8GB memory)
   - **Boot disk**: 
     - Operating System: Ubuntu 20.04 LTS
     - Boot disk type: SSD persistent disk (10GB is enough)
   - **Firewall**: Allow HTTP and HTTPS traffic
   - **Advanced options** → **Management** → **Availability policies**:
     - Automatic restart: ON
     - On host maintenance: Migrate VM instance
5. Click "Create"

### Step 2: Set Up Your VM

1. Once the VM is running, click the "SSH" button to connect to it
2. Update the system and install required packages:
   ```
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv git
   ```

3. Create a folder for your bot and download the code:
   ```
   mkdir options-wizard
   cd options-wizard
   ```

4. Now, either upload your files from Replit, or clone from GitHub if you've pushed your code there:
   ```
   # If using GitHub:
   git clone https://github.com/yourusername/options-wizard.git .
   
   # If uploading directly:
   # Use the Cloud Shell Editor (click the pencil icon in SSH window)
   # Or use SFTP with a tool like FileZilla
   ```

5. Set up Python environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install discord.py matplotlib numpy pandas python-dateutil python-dotenv pytz requests scipy streamlit trafilatura yfinance
   ```

6. Create your .env file with your secrets:
   ```
   echo "DISCORD_TOKEN=your_discord_token" > .env
   echo "POLYGON_API_KEY=your_polygon_api_key" >> .env
   ```

### Step 3: Set Up Your Bot as a Service

1. Create a systemd service file:
   ```
   sudo nano /etc/systemd/system/options-wizard.service
   ```

2. Copy this content into the file (replace "your-username" with your actual username):
   ```
   [Unit]
   Description=OptionsWizard Discord Bot
   After=network.target

   [Service]
   User=your-username
   WorkingDirectory=/home/your-username/options-wizard
   ExecStart=/home/your-username/options-wizard/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Save the file (Ctrl+O, then Enter, then Ctrl+X)

4. Enable and start the service:
   ```
   sudo systemctl enable options-wizard
   sudo systemctl start options-wizard
   ```

5. Check that it's running:
   ```
   sudo systemctl status options-wizard
   ```

### Step 4: Set Up Basic Monitoring

1. Go to Google Cloud Console → "Monitoring"
2. Navigate to "Alerting" → "Create Policy"
3. Set up basic alerts:
   - CPU usage exceeds 80% for 5 minutes
   - Memory usage exceeds 80% for 5 minutes
   - Disk space below 20%
4. Add your email to receive notifications

### Step 5: Accessing Your Streamlit Admin Interface

1. By default, your Streamlit app runs on port 5000. To access it securely:
   ```
   sudo apt install -y nginx
   ```

2. Set up an nginx config:
   ```
   sudo nano /etc/nginx/sites-available/options-wizard
   ```

3. Add this configuration:
   ```
   server {
       listen 80;
       server_name your-server-ip-or-domain;

       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. Enable the site:
   ```
   sudo ln -s /etc/nginx/sites-available/options-wizard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. Now you can access your Streamlit admin interface at http://your-server-ip

## Option 2: Google Cloud Run (Advanced - Better for Scaling)

### Step 1: Set Up Your Local Environment

1. Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Open a terminal and log in:
   ```
   gcloud auth login
   ```
3. Create a new project or set your existing project:
   ```
   gcloud projects create [PROJECT_ID] --name="OptionsWizard"
   # or
   gcloud config set project [PROJECT_ID]
   ```
4. Enable required APIs:
   ```
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

### Step 2: Prepare Your Application

1. Download your code from Replit to your local machine
2. Make sure you have the Dockerfile in your project root (the one we created earlier)

### Step 3: Build and Deploy

1. Build your container:
   ```
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/options-wizard
   ```

2. Deploy to Cloud Run:
   ```
   gcloud run deploy options-wizard \
     --image gcr.io/[PROJECT_ID]/options-wizard \
     --platform managed \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1 \
     --set-env-vars="DISCORD_TOKEN=your_discord_token,POLYGON_API_KEY=your_polygon_api_key"
   ```

3. Set minimum instances to 1:
   ```
   gcloud run services update options-wizard \
     --min-instances=1 \
     --max-instances=5
   ```

### Step 4: Set Up Monitoring for Cloud Run

1. Go to Google Cloud Console → "Monitoring"
2. Navigate to "Alerting" → "Create Policy"
3. Set up alerts for Cloud Run services:
   - Instance count at maximum for more than 30 minutes (indicates you might need to raise the limit)
   - Error rates above threshold
   - High latency in responses

## Troubleshooting Tips

### If Your Bot Isn't Connecting to Discord

1. Check the service logs:
   ```
   # For Compute Engine:
   sudo journalctl -u options-wizard.service

   # For Cloud Run:
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=options-wizard"
   ```

2. Make sure your environment variables are correct:
   ```
   # For Compute Engine:
   sudo systemctl stop options-wizard
   nano .env  # Edit your environment variables
   sudo systemctl start options-wizard

   # For Cloud Run:
   gcloud run services update options-wizard \
     --set-env-vars="DISCORD_TOKEN=corrected_token,POLYGON_API_KEY=corrected_key"
   ```

### If Your Streamlit Admin Interface Isn't Working

1. Check if Streamlit is running:
   ```
   ps aux | grep streamlit
   ```

2. Check the firewall settings in GCP console
3. Make sure you've configured nginx correctly (for Compute Engine)

## Cost Saving Tips

1. For Compute Engine, use a smaller instance during testing
2. For Cloud Run, set a budget alert to notify you if costs are higher than expected
3. Consider shutting down resources when not actively using them during development

## Backup Strategy

1. For Compute Engine, create a snapshot schedule:
   ```
   gcloud compute disks snapshot options-wizard-disk --snapshot-names=options-wizard-backup --zone=your-zone
   ```

2. For Cloud Run, ensure your important data is persisted to a database or storage bucket