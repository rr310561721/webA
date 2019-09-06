import time

from models.topic import Topic

from sqlalchemy import Unicode, Column

from models import db, SQLMixin


class Board(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)

    @classmethod
    def update(cls, form):
        board_id = form.get('board_id', '')
        del form['board_id']
        super().update(board_id, **form)

    @classmethod
    def delete(cls, id):
        # 删除板块下所有帖子
        ts = Topic.all(board_id=id)

        for t in ts:
            Topic.delete(t.id)
        # 删除板块
        super().delete(id)
        return '成功删除'