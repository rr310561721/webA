from flask import (
    render_template,
    request,
    redirect,
    url_for,
    Blueprint,
)

from utils import log

from routes import (
    current_user,
    user_role,
)

from models.board import Board

main = Blueprint('board', __name__)


@main.route("/admin")
@user_role
def index():
    bs = Board.all()
    u = current_user()
    log('進入管理員頁面', u)
    return render_template('board/admin_index.html', bs=bs)


@main.route("/add", methods=["POST"])
@user_role
def add():
    form = request.form
    u = current_user()
    m = Board.new(form)
    return redirect(url_for('.index'))


@main.route("/delete")
@user_role
def delete():
    board_id = int(request.args.get('board_id'))
    Board.delete(board_id)
    return redirect(url_for('.index'))


@main.route("/update", methods=["POST"])
@user_role
def update():
    form = request.form.to_dict()
    Board.update(form)
    return redirect(url_for('.index'))
