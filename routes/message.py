from flask_mail import Message, Mail
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *

from models.message import Messages
from models.user import User
from config import admin_mail

main = Blueprint('mail', __name__)
mail = Mail()


@main.route('/')
@login_required
def index():
    u = current_user()

    sent_mail = Messages.all(sender_id=u.id)
    received_mail = Messages.all(receiver_id=u.id)
    token = new_csrf_token()
    t = render_template(
        'mail/index.html',
        send=sent_mail,
        received=received_mail,
        token=token,
    )
    return t


@main.route("/add", methods=["POST"])
@login_required
@csrf_required
def add():
    # 发邮件的路由
    form = request.form.to_dict()
    receiver = User.one(username=form['receiver_name'])
    u = current_user()
    del form['receiver_name']
    form['receiver_id'] = receiver.id
    form['sender_id'] = u.id

    # 发邮件
    # r = User.one(id=form['receiver_id'])
    # m = Message(
    #     subject=form['title'],
    #     body=form['content'],
    #     sender=admin_mail,
    #     recipients=[r.email]
    # )
    # mail.send(m)

    m = Messages.new(form)
    return redirect(url_for('.index'))


@main.route('/view/<int:id>')
@login_required
def view(id):
    message = Messages.one(id=id)
    u = current_user()
    sender = User.one(id=message.sender_id)
    receiver = User.one(id=message.receiver_id)
    if u.id in [message.receiver_id, message.sender_id]:
        return render_template('mail/detail.html', message=message, user=u, sender=sender, receiver=receiver)
    else:
        return redirect(url_for('.index'))
