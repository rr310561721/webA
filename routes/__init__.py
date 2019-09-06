import uuid
from functools import wraps

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    abort,
    send_from_directory
)
from utils import log
from models.user import User
from models.user_role import UserRole


def current_user():
    uid = session.get('user_id', '')
    u = User.one(id=uid)
    return u


def csrf_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args['token']
        u = current_user()
        if token in session and session[token] == u.id:
            session.pop(token)
            return f(*args, **kwargs)
        else:
            abort(401)

    return wrapper


def new_csrf_token():
    u = current_user()
    token = str(uuid.uuid4())
    session[token] = u.id
    return token


def login_required(f):
    # 验证用户是否登录
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if u is None:
            return redirect(url_for('index.index'))
        else:
            return f(*args, **kwargs)

    return wrapper


def same_user_required(func):
    # 对用户信息进行修改，需要进行权限认证
    @wraps(func)
    def inner(*args, **kwargs):
        if request.method == 'POST':
            user_id = int(request.form.get('user_id'))
        else:
            user_id = int(request.args.get('user_id'))

        u = current_user()
        print('user_id is {}'.format(user_id), type(user_id))
        print('u.id is {}'.format(u.id), type(u.id))
        if u is None:
            return redirect(url_for('index.index'))
        elif u.id == user_id:
            return func(*args, **kwargs)
        else:
            return render_template('404.html')

    return inner


def user_role(f):
    # 用户权限
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if u is None:
            return redirect(url_for('topic.index'))
        elif u.role == UserRole.admin:
            return f(*args, **kwargs)
        else:
            return render_template('404.html')

    return wrapper
