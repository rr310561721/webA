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

# cache = redis.StrictRedis()

from utils import log

main = Blueprint('index', __name__)

"""
主页页面的路由
主要是让用户登录
然后定向到topic/index
"""


@main.route("/")
def index():
    # 主页路由，登录的页面
    result = session.pop('result', None)

    log('result', result)

    return render_template('index.html', result=result)






