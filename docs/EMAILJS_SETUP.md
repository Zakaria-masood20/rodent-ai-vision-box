# EmailJS Setup Guide for Rodent Detection System

## Overview
EmailJS is a service that allows you to send emails directly from client-side code without needing an SMTP server. This guide will help you set up EmailJS for the Rodent Detection System as a replacement for Twilio SMS notifications.

## Why EmailJS?
- **No SMTP server required**: Works directly through EmailJS API
- **No complex authentication**: No need for app-specific passwords
- **Free tier available**: 200 emails per month for free
- **Easy setup**: Simple web-based configuration
- **Reliable delivery**: Uses established email providers
- **No toll-free verification**: Unlike Twilio, no phone number verification needed

## Step 1: Create EmailJS Account

1. Go to [https://www.emailjs.com](https://www.emailjs.com)
2. Click "Sign Up" and create a free account
3. Verify your email address

## Step 2: Add Email Service

1. In your EmailJS dashboard, click "Email Services"
2. Click "Add New Service"
3. Choose your email provider:
   - **Gmail** (recommended)
   - **Outlook**
   - **Yahoo**
   - **Custom SMTP**
4. Follow the connection steps for your provider:
   - For Gmail: You'll be redirected to Google to authorize EmailJS
   - For Outlook: You'll be redirected to Microsoft to authorize
5. Give your service a name (e.g., "RodentDetection")
6. Note down your **Service ID** (looks like: `service_xxxxxxx`)

## Step 3: Create Email Template

1. Go to "Email Templates" in the dashboard
2. Click "Create New Template"
3. Set up your template as follows:

### Template Settings:
- **Name**: Rodent Alert Template
- **Subject**: 🚨 Rodent Alert: {{rodent_type}} Detected

### Template Content:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .alert-box { 
            border: 2px solid #ff0000; 
            padding: 20px; 
            border-radius: 10px;
            background-color: #fff5f5;
        }
        .details { margin: 15px 0; }
        .label { font-weight: bold; }
    </style>
</head>
<body>
    <div class="alert-box">
        <h2>🚨 Rodent Detection Alert</h2>
        
        <div class="details">
            <span class="label">Type:</span> {{rodent_type}}
        </div>
        
        <div class="details">
            <span class="label">Detection Time:</span> {{detection_time}}
        </div>
        
        <div class="details">
            <span class="label">Confidence Level:</span> {{confidence}}
        </div>
        
        <div class="details">
            <span class="label">Message:</span><br>
            {{message}}
        </div>
        
        <hr>
        <p><em>This alert was sent from the Rodent Detection System</em></p>
    </div>
</body>
</html>
```

4. In the "To Email" field, enter: `{{to_email}}`
5. In the "From Name" field, enter: `{{from_name}}`
6. Save the template
7. Note down your **Template ID** (looks like: `template_xxxxxxx`)

## Step 4: Get Your API Keys

1. Go to "Account" → "API Keys" in the dashboard
2. Note down your:
   - **Public Key** (starts with a few characters)
   - **Private Key** (optional, for extra security)

## Step 5: Configure the Rodent Detection System

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your EmailJS credentials:
   ```env
   # EmailJS Configuration
   EMAILJS_SERVICE_ID=service_xxxxxxx
   EMAILJS_TEMPLATE_ID=template_xxxxxxx
   EMAILJS_PUBLIC_KEY=your_public_key_here
   EMAILJS_PRIVATE_KEY=your_private_key_here  # Optional
   EMAILJS_TO_EMAIL=your-email@example.com
   ```

3. Update `config/config.yaml` to use EmailJS:
   ```yaml
   alerts:
     enabled_channels:
       - "emailjs"  # Enable EmailJS
       # - "sms"    # Disable Twilio SMS
   ```

## Step 6: Test the Configuration

Run the test script to verify everything is working:

```bash
python test_emailjs.py
```

You should receive a test email if everything is configured correctly.

## Step 7: Template Variables

The following variables are available in your EmailJS template:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{to_email}}` | Recipient email address | user@example.com |
| `{{from_name}}` | Sender name | Rodent Detection System |
| `{{rodent_type}}` | Type of rodent detected | Norway Rat |
| `{{detection_time}}` | Time of detection | 2024-01-15 03:45:23 PM |
| `{{confidence}}` | Detection confidence | 95% |
| `{{message}}` | Full alert message | 🚨 RODENT ALERT! Norway Rat detected... |
| `{{image_data}}` | Base64 encoded image | (image data) |
| `{{image_name}}` | Image filename | detection_2024_01_15.jpg |

## Troubleshooting

### Email not received?
1. Check spam/junk folder
2. Verify all credentials are correct in `.env`
3. Check EmailJS dashboard for send history and errors
4. Ensure you haven't exceeded the free tier limit (200 emails/month)

### "Service not found" error?
- Double-check your Service ID in the `.env` file
- Make sure the service is active in EmailJS dashboard

### "Template not found" error?
- Verify your Template ID in the `.env` file
- Ensure the template is saved and active

### Rate limiting?
- Free tier allows 200 emails per month
- Consider upgrading if you need more

## Advanced Features

### Adding Images to Emails
The system automatically encodes detection images as base64 and includes them in the email. To display them in your template:

```html
{{#if image_data}}
<div class="details">
    <span class="label">Detection Image:</span><br>
    <img src="data:image/jpeg;base64,{{image_data}}" style="max-width: 500px; margin-top: 10px;">
</div>
{{/if}}
```

### Multiple Recipients
To send to multiple recipients, you can:
1. Use CC/BCC fields in the EmailJS template
2. Create multiple templates for different recipients
3. Modify the code to send multiple emails

## Security Notes

1. **Never commit credentials**: Keep your `.env` file out of version control
2. **Use Private Key**: For production, use both public and private keys
3. **Monitor usage**: Check your EmailJS dashboard regularly for unusual activity
4. **Rotate keys**: Periodically regenerate your API keys

## Support

- EmailJS Documentation: [https://www.emailjs.com/docs/](https://www.emailjs.com/docs/)
- EmailJS Support: support@emailjs.com
- System Issues: Check the project's GitHub repository

## Migration from Twilio

If you're migrating from Twilio SMS:
1. Keep your Twilio configuration as backup
2. Test EmailJS thoroughly before disabling Twilio
3. You can run both simultaneously by enabling both in `config.yaml`:
   ```yaml
   enabled_channels:
     - "emailjs"
     - "sms"
   ```