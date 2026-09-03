import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.smtp_user
            msg['To'] = to_email
            
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_job_alert(
        self,
        to_email: str,
        alert_name: str,
        jobs: List[dict]
    ) -> bool:
        """Send a job alert email"""
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4F46E5; color: white; padding: 20px; text-align: center; }
                .job-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; }
                .job-title { font-size: 18px; font-weight: bold; color: #4F46E5; }
                .company { color: #666; font-size: 14px; }
                .salary { color: #10B981; font-weight: bold; }
                .skills { margin-top: 10px; }
                .skill-tag { background-color: #E5E7EB; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
                .button { display: inline-block; background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                .footer { margin-top: 20px; text-align: center; color: #999; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Job Alert: {{ alert_name }}</h1>
                </div>
                
                <p>We found {{ jobs|length }} new jobs matching your alert:</p>
                
                {% for job in jobs %}
                <div class="job-card">
                    <div class="job-title">{{ job.title }}</div>
                    <div class="company">{{ job.company_name }}</div>
                    <div class="location">📍 {{ job.location }}</div>
                    {% if job.salary_display %}
                    <div class="salary">💰 {{ job.salary_display }}</div>
                    {% endif %}
                    <div class="skills">
                        {% for skill in job.skills[:5] %}
                        <span class="skill-tag">{{ skill }}</span>
                        {% endfor %}
                    </div>
                    <p style="margin-top: 10px;">
                        <a href="{{ job.source_url }}" class="button">View Job</a>
                    </p>
                </div>
                {% endfor %}
                
                <div class="footer">
                    <p>You're receiving this because you set up a job alert on RemoteJobHub.</p>
                    <p><a href="#">Unsubscribe</a> | <a href="#">Manage Alerts</a></p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        html_content = template.render(alert_name=alert_name, jobs=jobs)
        
        return self.send_email(
            to_email=to_email,
            subject=f"🔔 {len(jobs)} New Jobs: {alert_name}",
            html_content=html_content
        )
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send a welcome email to new users"""
        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4F46E5; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .button { display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }
                .feature { margin: 15px 0; padding: 10px; background-color: #F3F4F6; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to RemoteJobHub! 🎉</h1>
                </div>
                
                <div class="content">
                    <p>Hi {{ username }},</p>
                    
                    <p>Welcome to RemoteJobHub - your new home for finding pure remote jobs!</p>
                    
                    <p>Here's what you can do:</p>
                    
                    <div class="feature">
                        <strong>🔍 Instant Search</strong>
                        <p>Search through thousands of remote jobs with powerful filters.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>🔔 Job Alerts</strong>
                        <p>Set up alerts to get notified when new jobs matching your criteria are posted.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>💼 Save Jobs</strong>
                        <p>Save interesting jobs and add notes for later.</p>
                    </div>
                    
                    <div class="feature">
                        <strong>🏢 Company Insights</strong>
                        <p>View company profiles, salary data, and remote culture ratings.</p>
                    </div>
                    
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="http://localhost:3000" class="button">Start Exploring Jobs</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """)
        
        html_content = template.render(username=username)
        
        return self.send_email(
            to_email=to_email,
            subject="Welcome to RemoteJobHub! 🎉",
            html_content=html_content
        )


email_service = EmailService()