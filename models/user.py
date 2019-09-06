import hashlib

from sqlalchemy import Column, String, Text, Enum

import config
import secret
from models import SQLMixin, db
from models.user_role import UserRole


class User(SQLMixin, db.Model):
    __tablename__ = 'User'
    """
    User 是一个保存用户数据的 model
    现在只有两个属性 username 和 password
    """
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100), nullable=False, default='/user/avatars/0.jpg')
    email = Column(String(50), nullable=False, default=config.test_mail)
    note = Column(String(500), nullable=False, default=' 这家伙很懒，什么个性签名都没有留下。  ')
    role = Column(Enum(UserRole), nullable=False, default=UserRole.normal)

    def add_default_value(self):
        super().add_default_value()
        self.password = self.salted_password(self.password)

    @staticmethod
    def salted_password(password, salt='$!@><?>HUI&DWQa`'):
        salted = hashlib.sha256((password + salt).encode('ascii')).hexdigest()
        return salted

    @classmethod
    def register(cls, form):
        name = form.get('username', '')
        pwd = form.get('password', '')

        if User.one(username=name) is not None:
            return '用户名已存在'
        else:
            if len(name) > 2 and len(pwd) > 2:
                form['password'] = User.salted_password(form['password'])
                User.new(form)
                return '注册成功'
            else:
                return '用户名长度需要大于2，密码长度需要大于2'


    @classmethod
    def validate_login(cls, form):
        query = dict(
            username=form['username'],
            password=User.salted_password(form['password']),
        )

        if User.one(**query) is not None:
            return User.one(**query)
        else:
            return None

    # @classmethod
    # def validate_login(cls, form):
    #     query = dict(
    #         username=form['username'],
    #         password=User.salted_password(form['password']),
    #     )
    #     print('validate_login', form, query)
    #     return User.one(**query)

    @classmethod
    def update_password(cls, uid, form):
        old_password = form["old_pass"]
        new_password = form["new_pass"]
        u = cls.one(id=uid)
        if u.password == cls.salted_password(old_password):
            if len(new_password) > 2:
                password = cls.salted_password(new_password)
                super().update(uid, password=password)
                return '修改成功'
            else:
                return '密码长度需要大于2'
        else:
            return '当前密码不正确'
