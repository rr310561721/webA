from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from routes import *
from utils import log
from models.topic import Topic
from models.board import Board

main = Blueprint('topic', __name__)


@main.route("/")
@login_required
def index():
    # 显示所有帖子的主页面路由
    u = current_user()
    board_id = int(request.args.get('board_id', -1))
    if board_id == -1:
        ms = Topic.all()
    else:
        ms = Topic.all(board_id=board_id)

    # log('所有帖子内容', ms)
    token = new_csrf_token()
    bs = Board.all()
    return render_template(
        "topic/index.html",
        ms=ms,
        token=token,
        bs=bs,
        bid=board_id,
        user=u,
    )


@main.route('/<int:id>')
@login_required
def detail(id):
    # 帖子详情页面路由
    m = Topic.get(id)
    # 传递 topic 的所有 reply 到 页面中
    u = current_user()
    board = Board.one(id=m.board_id)
    token = new_csrf_token()
    return render_template("topic/detail.html", topic=m, user=u, board=board, token=token)


@main.route("/delete")
@same_user_required
@csrf_required
def delete():
    # 删除topic的路由
    topic_id = int(request.args.get('id'))
    u = current_user()
    print('删除 topic 用户是', u, id)
    Topic.delete(topic_id)
    return redirect(url_for('.index'))


@main.route("/new")
@login_required
def new():
    # 创建帖子的页面路由
    board_id = int(request.args.get('board_id'))
    bs = Board.all()
    u = current_user()
    # return render_template("topic/new.html", bs=bs, bid=board_id)
    token = new_csrf_token()
    return render_template("topic/new.html", bs=bs, token=token, bid=board_id, user=u)


@main.route("/add", methods=["POST"])
@same_user_required
@csrf_required
def add():
    # 创建帖子的路由
    form = request.form.to_dict()
    u = current_user()
    Topic.new(form, user_id=u.id)
    return redirect(url_for('.index'))
