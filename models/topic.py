import time

from sqlalchemy import String, Integer, Column, Text, UnicodeText, Unicode

from models import SQLMixin, db
from models.user import User
from models.reply import Reply


class Topic(SQLMixin, db.Model):
    views = Column(Integer, nullable=False, default=0)
    title = Column(Unicode(50), nullable=False)
    content = Column(UnicodeText, nullable=False)
    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    @classmethod
    def new(cls, form, user_id):
        form['user_id'] = user_id
        m = super().new(form)
        return m

    @classmethod
    def get(cls, id):
        m = cls.one(id=id)
        m.views += 1
        m.save()
        return m

    @classmethod
    def all(cls, **kwargs):
        ms = cls.query.filter_by(**kwargs).all()
        return ms

    def user(self):
        u = User.one(id=self.user_id)
        return u

    def replies(self):
        ms = Reply.all(topic_id=self.id)
        return ms

    def reply_count(self):
        count = len(self.replies())
        return count

    @classmethod
    def delete(cls, id):
        # 删除帖子下所有评论
        rs = Reply.all(topic_id=id)
        for r in rs:
            Reply.delete(r.id)
        # 删除帖子
        super().delete(id)
        return '成功删除'
