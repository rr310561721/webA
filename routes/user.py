import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    session,
    url_for,
    Blueprint,
    make_response,
    abort,
    send_from_directory,
)
from werkzeug.utils import secure_filename

from models.reply import Reply
from models.topic import Topic
from models.user import User
from routes import *

import json

# import redis

# cache = redis.StrictRedis()

from utils import log

main = Blueprint('user', __name__)

"""
    关于用户的路由
    注册
    登录
    设置
    签名
    密码修改
    头像修改
    用户主页
"""


@main.route("/register/view")
def register_view():
    # 注册页面路由
    result = session.pop('result', None)

    log('result', result)

    return render_template('user/register.html', result=result)


@main.route("/register", methods=['POST'])
def register():
    # 注册的路由
    form = request.form.to_dict()
    # 用类函数来判断
    result = User.register(form)

    session['result'] = result
    return redirect(url_for('.register_view'))


@main.route("/login/view")
def login_view():
    # 登录页面路由
    result = session.pop('result', None)
    log('result', result)

    return render_template('user/login.html', result=result)


@main.route("/login", methods=['POST'])
def login():
    # 登录的路由
    form = request.form
    u = User.validate_login(form)
    if u is None:
        session['result'] = '用户名或密码错误'
        return redirect(url_for('index.index'))
    else:
        # session 中写入 user_id
        session['user_id'] = u.id
        # 设置 cookie 有效期为 永久
        session.permanent = True
        # 转到 topic.index 页面
        return redirect(url_for('topic.index'))


@main.route("/logout")
@login_required
def logout():
    # 退出登录的路由
    session.pop('user_id')
    return redirect(url_for('index.index'))


@main.route('/set')
@login_required
def set_view():
    # 设置的页面路由
    u = current_user()
    result = session.pop("update_password_result", None)
    token = new_csrf_token()
    if u is None:
        return redirect(url_for('.index'))
    else:
        return render_template(
            'user/set.html',
            user=u,
            result=result,
            token=token,
        )


@main.route('/update/signature', methods=['POST'])
@same_user_required
@csrf_required
def update_signature():
    # 设置页面，修改用户签名的路由
    form = request.form.to_dict()
    u = current_user()
    User.update(u.id, **form)
    return redirect(url_for('.set_view'))


@main.route('/update/password', methods=['POST'])
@same_user_required
@csrf_required
def update_password():
    # 设置页面，保存密码修改的路由
    form = request.form.to_dict()
    u = current_user()
    user_id = u.id

    result = User.update_password(user_id, form)

    session["update_password_result"] = result
    return redirect(url_for(".set_view"))


@main.route('/update/avatar', methods=['POST'])
@same_user_required
@csrf_required
def avatar_add():
    # 设置页面，更换头像的路由
    file = request.files['avatar']

    # ../../root/.ssh/authorized_keys
    # filename = secure_filename(file.filename)
    suffix = file.filename.split('.')[-1]
    filename = '{}.{}'.format(str(uuid.uuid4()), suffix)
    path = os.path.join('avatars', filename)
    file.save(path)

    u = current_user()
    User.update(u.id, avatar='/user/avatars/{}'.format(filename))

    return redirect(url_for('.set_view'))


@main.route('/avatars/<filename>')
def avatar(filename):
    # 处理头像图片的路由

    # 不要直接拼接路由，不安全，比如
    # http://localhost:2000/images/..%5Capp.py
    # path = os.path.join('images', filename)
    # print('images path', path)
    # return open(path, 'rb').read()
    return send_from_directory('avatars', filename)


@main.route('/<username>')
@login_required
def profile(username):
    # 用户主页的页面处理路由
    user = User.one(username=username)

    if user is None:
        return redirect(url_for('.index'))
    else:
        topics_cj = Topic.all(user_id=user.id)
        topics_cj = sorted(topics_cj, key=lambda x: x.created_time, reverse=True)

        rs = Reply.all(user_id=user.id)
        rs = sorted(rs, key=lambda x: x.created_time, reverse=True)
        topics_cy = [Topic.get(r.topic_id) for r in rs]

        return render_template('user/profile.html', user=user, topics_cj=topics_cj, topics_cy=topics_cy)

