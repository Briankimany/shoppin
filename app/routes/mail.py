from flask import Blueprint, current_app, request, render_template, redirect, url_for, session, jsonify
from flask.views import MethodView
from flask_mail import Message
from app.services.mail import mail
from app.routes.logger import LOG, bp_error_logger
from datetime import datetime

mail_bp = Blueprint('mail', __name__, url_prefix="/mail")


class MailService:
    @staticmethod
    def send_email(to, subject, template):
        """Send email using Flask-Mail"""
        with current_app.app_context():  
            try:
                msg = Message(
                    subject,
                    recipients=[to],
                    html=template,
                    sender=current_app.config['MAIL_DEFAULT_SENDER']
                )
                LOG.MAIL_LOGGER.debug("Sending email to {} :subject {}".format(to, subject))
                mail.send(msg)
                LOG.MAIL_LOGGER.debug(f"Email subject {subject} sent to {to}")
                return True
            except Exception as e:
                LOG.MAIL_LOGGER.error(f"Mail error: {str(e)}")
                return False

    @staticmethod
    def send_reset_email(recipient, reset_link):
        html = render_template(
            'mail/password_reset.html',
            reset_link=reset_link,
            unsubscribe_link=url_for('mail.unsubscribe', _external=True),
            contact_link=url_for('mail.contact', _external=True)
        )
        return MailService.send_email(to=recipient, subject="Password Reset Request", template=html)
    
    @staticmethod
    def send_account_activation_link(activation_url ,recepient ,return_json = True ,expiration=24):
        
        LOG.USER_LOGGER.debug("[EMAIL] sending email verification")
        LOG.USER_LOGGER.debug(f"[EMAIL] to: {recepient} link:{activation_url}")

        html_body = render_template('mail/activate_account.html',
                          activation_link=activation_url,
                          expiration_hours=expiration, 
                          current_year=datetime.now().year,
                        unsubscribe_link=url_for('mail.unsubscribe', _external=True),
                        contact_link=url_for('mail.contact', _external=True)
        )
                    
        mail_sent = MailService.send_email(
            to = recepient,
            subject="Account Activation",
            template=html_body
        )

        LOG.USER_LOGGER.debug(f"Response from sending email {mail_sent}")
        if not return_json:
            return mail_sent
        
        return jsonify({"message":"success" if mail_sent else "error",
                        'data':"Mail sent" if mail_sent else "Could not send reset link"})
    


    @staticmethod
    def send_general_notice(name, subject, message, recepient):
        html = render_template(
            '/mail/general_notice.html',
            subject=subject,
            name=name,
            message_body=message,
            unsubscribe_link=url_for('mail.unsubscribe', _external=True),
            contact_link=url_for('mail.contact', _external=True)
        )
        return MailService.send_email(to=recepient, subject=subject, template=html)


class ContactView(MethodView):
    def get(self):
        return render_template('mail/contact.html')


class UnsubscribeView(MethodView):
    def get(self):
        pass


class SendTestEmailView(MethodView):
    def get(self):
        default_recipient = "playpit@proton.me"
        default_subject = "Testing Email Service"
        return render_template('mail/email_form.html',
                            default_recipient=default_recipient,
                            default_subject=default_subject)

    def post(self):
        default_recipient = "playpit@proton.me"
        default_subject = "Testing Email Service"
        
        recipient = request.form.get('recipient', default_recipient)
        subject = request.form.get('subject', default_subject)
        message = request.form['message']
        
        mail_sent = MailService.send_general_notice(
            name=session.get("user_id"),
            subject=subject,
            message=message,
            recepient=recipient
        )
        return jsonify({"message":"success" if mail_sent else "error" ,
                        "data":"Email sent" if mail_sent else "Could not send email"})


class SendEmailAPI(MethodView):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ['recipient', 'subject', 'body']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        success = MailService.send_email(
            to=data['recipient'],
            subject=data['subject'],
            template=data['body']
        )
        
        if success:
            return jsonify({"message": "success", "data":"Email sent successfully"}), 200
        return jsonify({"message":"error","data": "Failed to send email"}), 500

# Register views
mail_bp.add_url_rule('/contact', view_func=ContactView.as_view('contact'))
mail_bp.add_url_rule('/unsubscribe', view_func=UnsubscribeView.as_view('unsubscribe'))
mail_bp.add_url_rule('/send-test-email', view_func=SendTestEmailView.as_view('send_test_email'))
mail_bp.add_url_rule('/send-email', view_func=SendEmailAPI.as_view('send_email_api'))