# Lab-Monitoring-System
The Automated Lab Monitoring System is a cloud-based solution that collects and monitors system information from 50+ lab PCs automatically. A Python script runs at startup, sending data to AWS (API Gateway + Lambda + DynamoDB), while a Streamlit dashboard provides real-time status and alerts. This project reduces manual effort, ensures PCs are always ready for students, and demonstrates practical use of Python, Cloud, and Automation in IT infrastructure management.

🔗 Demo: lab-monitoring-system.streamlit.app

Username: jetking

password: jetking@raj

----

# Goal: 
Monitor 50+ lab PCs automatically. Collect hardware, OS, software, and network details. Send this data to AWS and display it on a dashboard.

----

# Core Components:
Client side (system.py) → Runs on every PC, collects info. 

Cloud side (AWS) → Stores and processes data.

Streamlit → Monitoring System.

Automation → Runs automatically on system boot.

----

# Before you begin, ensure you have:

•	AWS Account (Free Tier is enough) -  https://aws.amazon.com/console

•	Python 3.8+ installed on lab PCs -  https://www.python.org/downloads
