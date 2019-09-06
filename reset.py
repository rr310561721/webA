from sqlalchemy import create_engine

import secret
from app import configured_app
from models import db
from models.board import Board
from models.reply import Reply
from models.topic import Topic
from models.user import User
from models.user_role import UserRole
import gevent

def reset_database():
    url = 'mysql+pymysql://root:{}@localhost/?charset=utf8mb4'.format(secret.database_password)
    e = create_engine(url, echo=True)

    with e.connect() as c:
        c.execute('DROP DATABASE IF EXISTS webA')
        c.execute('CREATE DATABASE webA CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        c.execute('USE webA')

    db.metadata.create_all(bind=e)


def generate_fake_date():
    form1 = dict(
        username='test',
        password='1234',
        role=UserRole.admin,
    )
    User.register(form1)

    form2 = dict(
        username='Ayu',
        password='123',
        role=UserRole.admin,
    )
    User.register(form2)

    form3 = dict(
        title='电影',
    )
    form4 = dict(
        title='游戏',
    )
    form5 = dict(
        title='水区',
    )
    b = Board.new(form3)
    b1 = Board.new(form4)
    b2 = Board.new(form5)
    with open('markdown_demo.md', encoding='utf8') as f:
        content = f.read()
    topic_form = dict(
        title='markdown demo',
        board_id=b.id,
        content=content
    )

    u = User.one(username='test')
    for i in range(10):
        print('begin topic <{}>'.format(i))
        t = Topic.new(topic_form, u.id)

        reply_form = dict(
            content='reply test',
            topic_id=t.id,
        )
        for j in range(5):
            Reply.new(reply_form, u.id)


if __name__ == '__main__':
    app = configured_app()
    with app.app_context():
        reset_database()
        generate_fake_date()
