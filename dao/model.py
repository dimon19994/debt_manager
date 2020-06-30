from flask_sqlalchemy import SQLAlchemy
from app import app
from flask_security import RoleMixin, UserMixin

db = SQLAlchemy(app)

user_have_roles = db.Table('user_have_role',
                          db.Column("user_id", db.Integer(), db.ForeignKey('orm_user.id')),
                          db.Column("role_id", db.Integer(), db.ForeignKey('orm_role.id'))
                          )


Orm_Friend = db.Table('orm_friend',
                      db.Column('id_o', db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True),
                      db.Column('id_f', db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True)
                      )


# class OrmParticipant(db.Model):
#     __tablename__ = 'orm_participant'
#     person_di = db.Column(db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True)
#     event_id = db.Column(db.Integer(), db.ForeignKey('orm_event.id'), primary_key=True)

OrmParticipant = db.Table('orm_participant',
    db.Column('person_di', db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True),
    db.Column('event_id', db.Integer(), db.ForeignKey('orm_event.id'), primary_key=True)
)


class OrmPay(db.Model):
    __tablename__ = 'orm_pay'
    check_di = db.Column(db.Integer(), db.ForeignKey('orm_check.id'), primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True)
    sum = db.Column(db.Float(), nullable=False)


class OrmDebt(db.Model):
    __tablename__ = 'orm_debt'
    item_di = db.Column(db.Integer(), db.ForeignKey('orm_item.id'), primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey('orm_user.id'), primary_key=True)
    sum = db.Column(db.Float(), nullable=False)
    category = db.Column(db.String(100), nullable=False)


class OrmUser(db.Model, UserMixin):
    __tablename__ = 'orm_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    card = db.Column(db.String(16), nullable=True)
    active = db.Column(db.Boolean(), nullable=True)

    # id_ovn = db.relationship("ormFriend")
    # id_fri = db.relationship("ormFriend")

    right_nodes  = db.relationship(
        "OrmUser",
        secondary=Orm_Friend,
        primaryjoin=(id == Orm_Friend.c.id_o),
        secondaryjoin=(id == Orm_Friend.c.id_f),
        backref = 'parents'
    )

    roles = db.relationship("OrmRole", secondary=user_have_roles, backref=db.backref('person', lazy='dynamic'))

    event = db.relationship("OrmEvent", secondary=OrmParticipant)

    check_pay = db.relationship("OrmPay")
    check_deb = db.relationship("OrmDebt")


class OrmRole(db.Model, RoleMixin):
    __tablename__ = 'orm_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)


class OrmCheck(db.Model):
    __tablename__ = 'orm_check'
    id = db.Column(db.Integer, primary_key=True)
    sum = db.Column(db.Float(), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('orm_event.id'))

    item = db.relationship("OrmItem")
    user_pay = db.relationship("OrmPay")


class OrmItem(db.Model):
    __tablename__ = 'orm_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    check_id = db.Column(db.Integer, db.ForeignKey('orm_check.id'))

    user_deb = db.relationship("OrmDebt")



class OrmEvent(db.Model):
    __tablename__ = 'orm_event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

    check = db.relationship("OrmCheck")
    user = db.relationship("OrmUser",secondary=OrmParticipant)


db.create_all()