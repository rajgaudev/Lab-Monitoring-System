# Lab-Monitoring-System
As a Lab Assistant at Jetking, I was responsible for maintaining 50+ lab PCs, which required time-consuming manual checks for hardware, software, and performance issues. To solve this, I developed an Automated Lab PC Monitoring System that collects system data on every boot and sends it to AWS for centralized storage and monitoring. A real-time dashboard displays the health of all PCs and generates alerts for critical issues, allowing proactive maintenance. This project not only saved time and effort but also ensured that students always had reliable systems for their learning.

# Goal: 
Monitor 50+ lab PCs automatically. Collect hardware, OS, software, and network details. Send this data to AWS and display it on a dashboard.

# Core Components:
Client side (system.py) → Runs on every PC, collects info. 

Cloud side (AWS) → Stores and processes data.

Streamlit → Monitoring System.

Automation → Runs automatically on system boot.

# Project Setup Guide:
----
Before you begin, ensure you have:

•	AWS Account (Free Tier is enough) -  https://aws.amazon.com/console

•	Python 3.8+ installed on lab PCs -  https://www.python.org/downloads
