import json
from typing import Optional
from time import time
from datetime import datetime, timezone

import jwt
import rq
import redis
import sqlalchemy as sa
import sqlalchemy.orm as orm
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask_login import UserMixin

from app import db, login, current_app
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(obj.__tablename__, obj)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)

followers = sa.Table(
    "followers",
    db.metadata,
    sa.Column("follower_id", sa.Integer, sa.ForeignKey("user.id"),
              primary_key=True),
    sa.Column("followed_id", sa.Integer, sa.ForeignKey("user.id"),
              primary_key=True)
)


class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sa.String(64), index=True, unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(256))
    last_message_read_time: orm.Mapped[Optional[datetime]]

    posts: orm.WriteOnlyMapped["Post"] = orm.relationship(
        back_populates="author"
    )
    messages_sent: orm.WriteOnlyMapped["Message"] = orm.relationship(
        foreign_keys="Message.sender_id", back_populates="author")
    messages_received: orm.WriteOnlyMapped["Message"] = orm.relationship(
        foreign_keys="Message.recipient_id", back_populates="recipient")
    notifications: orm.WriteOnlyMapped["Notification"] = orm.relationship(
        back_populates="user")
    tasks: orm.WriteOnlyMapped["Task"] = orm.relationship(back_populates='user')

    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(256))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(default=lambda: datetime.now(timezone.utc))

    following: orm.WriteOnlyMapped["User"] = orm.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers"
    )
    followers: orm.WriteOnlyMapped["User"] = orm.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = orm.aliased(User)
        Follower = orm.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"], algorithm="HS256"
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config["SECRET_KEY"],
                            algorithms="HS256")["reset_password"]
        except:
            return
        return db.session.get(User, id)

    def unread_message_count(self):
        last_read_time = self.last_message_read_time or datetime(1990, 1, 1)
        query = sa.select(Message).where(Message.recipient == self,
                                         Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            query.subquery()))

    def add_notification(self, name, data):
        db.session.execute(self.notifications.delete().where(
            Notification.name == name))
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(f"app.tasks.{name}", self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        query = self.tasks.select().where(Task.complete == False)
        return db.session.scalars(query)

    def get_task_in_progress(self, name):
        query = self.tasks.select().where(Task.name == name,
                                          Task.complete == False)
        return db.session.scalar(query)

    def __repr__(self):
        return f"<User {self.username}>"


class Post(SearchableMixin, db.Model):
    __searchable__ = ["body"]

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sa.String(256))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(index=True,
                                                        default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id), index=True)
    author: orm.Mapped[User] = orm.relationship(back_populates="posts")

    language: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(5))

    def __repr__(self):
        return f"<Post {self.body}>"


class Message(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    sender_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id),
                                                   index=True)
    recipient_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id),
                                                      index=True)
    body: orm.Mapped[str] = orm.mapped_column(sa.String(256))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    author: orm.Mapped[User] = orm.relationship(
        foreign_keys="Message.sender_id",
        back_populates="messages_sent")

    recipient: orm.Mapped[User] = orm.relationship(
        foreign_keys="Message.recipient_id",
        back_populates="messages_received")

    def __repr__(self):
        return f"<Message: {self.body}>"


class Notification(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(128), index=True)
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id),
                                                 index=True)
    timestamp: orm.Mapped[float] = orm.mapped_column(index=True, default=time)
    payload_json: orm.Mapped[str] = orm.mapped_column(sa.Text)

    user: orm.Mapped[User] = orm.relationship(back_populates="notifications")

    def get_data(self):
        return json.loads(str(self.payload_json))


class Task(db.Model):
    id: orm.Mapped[str] = orm.mapped_column(sa.String(36), primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(sa.String(128), index=True)
    description: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(128))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id))
    complete: orm.Mapped[bool] = orm.mapped_column(default=False)

    user: orm.Mapped[User] = orm.relationship(back_populates='tasks')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100


@login.user_loader
def load_user(id: str):
    return db.session.get(User, int(id))
