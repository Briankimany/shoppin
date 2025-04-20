
from flask import Blueprint, current_app , request , render_template ,redirect ,url_for , session
from app.services.mail import mail
from flask_mail import Message

mail_bp = Blueprint('mail', __name__ ,url_prefix="/mail")



@mail_bp.route('/contact')
def contact():
    return render_template('mail/contact.html')

@mail_bp.route('/unsubscribe')
def unsubscribe():
    pass


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
            mail.send(msg)
            print(f"Email sent to {to}")
            return True
        except Exception as e:
            print(f"Mail error: {str(e)}")
            return False
        

def send_reset_email(recipient , reset_link):
   
    html = render_template(
        'mail/password_reset.html',
        reset_link=reset_link,
        unsubscribe_link=url_for('mail.unsubscribe', _external=True),
        contact_link=url_for('mail.contact', _external=True)
    )
    send_email(to=recipient, subject="Password Reset Request", template=html)


def send_general_notice(name, subject, message ,recepient):
    html = render_template(
        '/mail/general_notice.html',
        subject=subject,
        name=name,
        message_body=message,
        unsubscribe_link=url_for('mail.unsubscribe', _external=True),
        contact_link=url_for('mail.contact', _external=True)
    )
    send_email(to=recepient, subject=subject, template=html)



@mail_bp.route('/send-test-email', methods=['GET', 'POST'])
def send_test_email():
    default_recipient = "playpit@proton.me"
    default_subject = "Testing Email Service"

    if request.method == 'POST':
        recipient = request.form.get('recipient', default_recipient)
        subject = request.form.get('subject', default_subject)
        message = request.form['message']
        

        send_general_notice(name=session.get("user_id"), subject=subject, message=message ,recepient=recipient)
        return redirect(url_for('mail.send_test_email'))
    
    return render_template('mail/email_form.html',
                         default_recipient=default_recipient,
                         default_subject=default_subject)


