from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')

# Email templates
EMAIL_TEMPLATES = {
    'welcome': {
        'subject': 'Welcome to Our Platform!',
        'body': '''
        <h2>Welcome to Our Platform!</h2>
        <p>Dear Valued User,</p>
        <p>Thank you for joining our platform. We're excited to have you on board!</p>
        <p>Here's what you can expect:</p>
        <ul>
            <li>Regular updates and tips</li>
            <li>Exclusive content and offers</li>
            <li>Community support and resources</li>
        </ul>
        <p>Best regards,<br>The Team</p>
        '''
    },
    'newsletter': {
        'subject': 'Weekly Newsletter - Latest Updates',
        'body': '''
        <h2>Weekly Newsletter</h2>
        <p>Hello there!</p>
        <p>Here are this week's highlights:</p>
        <ul>
            <li><strong>New Features:</strong> We've added some exciting new functionality</li>
            <li><strong>Tips & Tricks:</strong> Learn how to make the most of our platform</li>
            <li><strong>Community Spotlight:</strong> Amazing stories from our users</li>
        </ul>
        <p>Stay tuned for more updates!</p>
        <p>Best,<br>The Newsletter Team</p>
        '''
    },
    'promotion': {
        'subject': 'Special Offer Just for You!',
        'body': '''
        <h2>Exclusive Offer Inside!</h2>
        <p>Hi there!</p>
        <p>We have a special offer just for you:</p>
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>🎉 Limited Time Offer</h3>
            <p>Get 20% off on all premium features!</p>
            <p><strong>Use code: SAVE20</strong></p>
        </div>
        <p>This offer is valid for the next 7 days only.</p>
        <p>Don't miss out!</p>
        <p>Cheers,<br>The Promotions Team</p>
        '''
    },
    'tips': {
        'subject': 'Daily Tips & Tricks',
        'body': '''
        <h2>Today's Tips & Tricks</h2>
        <p>Hello!</p>
        <p>Here's your daily dose of helpful tips:</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
            <h4>💡 Tip of the Day</h4>
            <p>Did you know you can customize your dashboard to show only the information you need? 
            Go to Settings > Dashboard to personalize your experience.</p>
        </div>
        <p>More tips coming your way soon!</p>
        <p>Happy learning,<br>The Tips Team</p>
        '''
    }
}

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email(recipient_email, email_type):
    """Send email to recipient"""
    try:
        # Check if email configuration is set
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            return False, "Email configuration not set. Please check your .env file."
        
        # Get email template
        template = EMAIL_TEMPLATES.get(email_type)
        if not template:
            return False, "Invalid email type"
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = template['subject']
        
        # Create HTML part
        html_part = MIMEText(template['body'], 'html')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, "Email sent successfully"
    
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

@app.route('/')
def index():
    """Main page with email form"""
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email_route():
    """Handle email sending request"""
    try:
        email = request.form.get('email', '').strip()
        email_type = request.form.get('email_type', '')
        
        # Validate input
        if not email:
            flash('Please enter your email address', 'error')
            return redirect(url_for('index'))
        
        if not is_valid_email(email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('index'))
        
        if email_type not in EMAIL_TEMPLATES:
            flash('Please select a valid email type', 'error')
            return redirect(url_for('index'))
        
        # Send email
        success, message = send_email(email, email_type)
        
        if success:
            flash(f'Email sent successfully to {email}!', 'success')
        else:
            flash(f'Failed to send email: {message}', 'error')
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/preview/<email_type>')
def preview_email(email_type):
    """Preview email template"""
    template = EMAIL_TEMPLATES.get(email_type)
    if not template:
        flash('Invalid email type', 'error')
        return redirect(url_for('index'))
    
    return render_template('preview.html', 
                         email_type=email_type, 
                         subject=template['subject'],
                         body=template['body'])

@app.route('/api/send-email', methods=['POST'])
def api_send_email():
    """API endpoint for sending emails"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        email_type = data.get('email_type', '')
        
        # Validate input
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not is_valid_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if email_type not in EMAIL_TEMPLATES:
            return jsonify({'error': 'Invalid email type'}), 400
        
        # Send email
        success, message = send_email(email, email_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Email sent successfully to {email}'
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)