# TODO add username
# TODO уникальность почты
# TODO уникальночсть ника


from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security, UserMixin, login_required, current_user
from flask_security.decorators import roles_accepted, roles_accepted
from flask_security.utils import hash_password
from sqlalchemy.sql import func

from forms.person_form import PersonForm
from forms.event_form import EventForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:01200120@localhost/debt_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'key'

app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['USER_EMAIL_SENDER_EMAIL'] = "noreply@example.com"

# db = SQLAlchemy(app)
from dao.model import *

user_datastore = SQLAlchemyUserDatastore(db, OrmUser, OrmRole)
security = Security(app, user_datastore)


@app.route('/', methods=['GET', 'POST'])
def root():
    return render_template('index.html')


@app.route('/person', methods=['GET'])
@login_required
def person():
    result = db.session.query(OrmUser).filter(OrmUser.id == current_user.id).all()

    return render_template('person.html', persons=result)


@app.route('/new_person', methods=['GET', 'POST'])
def new_person():
    form = PersonForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('person_form.html', form=form, form_name="New person", action="new_person")
        else:
            new_person = user_datastore.create_user(
                email=form.person_email.data,
                username=form.person_username.data,
                password=form.person_password.data,
                name=form.person_name.data,
                surname=form.person_surname.data,
                card=form.person_card.data,
            )

            role = db.session.query(OrmRole).filter(OrmRole.name == "User").one()

            new_person.roles.append(role)

            db.session.add(new_person)
            db.session.commit()

            return redirect(url_for('security.login'))

    return render_template('person_form.html', form=form, form_name="New person", action="new_person")


@app.route('/edit_person', methods=['GET', 'POST'])
@login_required
def edit_person():
    form = PersonForm()

    if request.method == 'GET':

        person_id = request.args.get('person_id')
        person = db.session.query(OrmUser).filter(OrmUser.id == person_id).one()

        form.person_id.data = person_id
        form.person_username.data = person.username
        form.person_email.data = person.email
        form.person_password.data = person.password
        form.person_name.data = person.name
        form.person_surname.data = person.surname
        form.person_card.data = person.card

        return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")


    else:

        if not form.validate():
            return render_template('person_form.html', form=form, form_name="Edit person", action="edit_person")
        else:
            person = db.session.query(OrmUser).filter(OrmUser.id == form.person_id.data).one()

            person.email = form.person_email.data
            person.username = form.person_username.data,
            person.password = hash_password(form.person_password.data)
            person.name = form.person_name.data
            person.surname = form.person_surname.data
            person.card = form.person_card.data

            db.session.commit()

            return redirect(url_for('person'))


@app.route('/delete_person', methods=['POST'])
@login_required
def delete_person():
    person_id = request.form['person_id']

    result = db.session.query(OrmUser).filter(OrmUser.id == person_id).one()

    db.session.delete(result)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/friends', methods=['GET'])
@login_required
def friends():
    all_0 = db.session.query(orm_friend.c.id_o.label("col_1"), orm_friend.c.id_f.label("col_2")).filter(
        orm_friend.c.id_o == current_user.id)
    all_1 = db.session.query(orm_friend.c.id_o.label("col_1"), orm_friend.c.id_f.label("col_2"))
    all_2 = db.session.query(orm_friend.c.id_f.label("col_1"), orm_friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    all_0 = db.session.query(orm_friend.c.id_o.label("col_1"), orm_friend.c.id_f.label("col_2")).filter(
        orm_friend.c.id_f == current_user.id)
    all_1 = db.session.query(orm_friend.c.id_f.label("col_1"), orm_friend.c.id_o.label("col_2")).filter(
        orm_friend.c.id_o == current_user.id)
    except_all = all_0.except_(all_1).with_entities("col_1")
    result_friends = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    return render_template('friends.html', persons=result_request, friends=result_friends)


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    person_id = request.form['person_id']

    dell = orm_friend.delete().where(or_(and_(orm_friend.c.id_o == current_user.id, orm_friend.c.id_f == person_id),
                                         and_(orm_friend.c.id_f == current_user.id, orm_friend.c.id_o == person_id)))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/except_friend', methods=['POST'])
@login_required
def except_friend():
    person_id = request.form['person_id']

    insert = orm_friend.insert().values(id_o=current_user.id, id_f=person_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/deny_friend', methods=['POST'])
@login_required
def deny_friend():
    person_id = request.form['person_id']

    dell = orm_friend.delete().where(and_(orm_friend.c.id_f == current_user.id, orm_friend.c.id_o == person_id))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/add_fiend', methods=['POST'])
@login_required
def add_fiend():
    person_id = request.form.get('username')

    frienf_id = db.session.query(OrmUser.id).filter(OrmUser.username == person_id).one()

    insert = orm_friend.insert().values(id_o=current_user.id, id_f=frienf_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('friends'))


@app.route('/events', methods=['GET'])
@login_required
def events():
    result = db.session.query(OrmEvent).join(OrmParticipant).filter(
        and_(OrmEvent.id == OrmParticipant.event_id, OrmParticipant.person_di == current_user.id)).all()

    return render_template('event.html', events=result)


@app.route('/detail_event', methods=['GET', 'POST'])
@login_required
def detail_event():
    events_id = request.args.get('event_id')

    participant_id = \
        db.session.query(OrmUser.id, OrmUser.name). \
            join(OrmParticipant).filter(OrmParticipant.person_di == OrmUser.id). \
            join(OrmEvent).filter(OrmEvent.id == OrmParticipant.event_id).all()

    pay_info = \
        db.session.query(func.coalesce(func.sum(OrmPay.sum), 0), OrmParticipant.person_di). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.event_id). \
            join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
            outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_di, OrmCheck.event_id == events_id,
                                   OrmParticipant.person_di == OrmPay.person_id)). \
            group_by(OrmParticipant.person_di).order_by(OrmParticipant.person_di).all()

    categorical_debt = \
        db.session.query(func.sum(OrmDebt.sum), OrmDebt.person_id, OrmDebt.category). \
            join(OrmItem, OrmDebt.item_di == OrmItem.id). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmDebt.person_id, OrmDebt.category).order_by(OrmDebt.person_id, OrmDebt.category).all()

    all_debt = \
        db.session.query(func.sum(OrmDebt.sum), OrmDebt.person_id). \
            join(OrmItem, OrmDebt.item_di == OrmItem.id). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmDebt.person_id).order_by(OrmDebt.person_id).all()

    categories = \
        db.session.query(OrmDebt.category). \
            join(OrmItem, OrmDebt.item_di == OrmItem.id). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmDebt.category).all()

    return render_template('event_table.html', people=participant_id, pay=pay_info, debt=categorical_debt,
                           categories=categories, all_debts=all_debt)


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    form = EventForm()

    all_0 = db.session.query(orm_friend.c.id_o.label("col_1"), orm_friend.c.id_f.label("col_2")).filter(
        orm_friend.c.id_o == current_user.id)
    all_1 = db.session.query(orm_friend.c.id_o.label("col_1"), orm_friend.c.id_f.label("col_2"))
    all_2 = db.session.query(orm_friend.c.id_f.label("col_1"), orm_friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    if request.method == 'POST':
        if not form.validate():
            return render_template('event_form.html', form=form, form_name="New event", action="new_event",
                                   friends=result_request)
        else:
            new_event = OrmEvent(
                name=form.event_name.data,
                place=form.event_place.data,
                date=form.event_date.data
            )

            db.session.add(new_event)
            db.session.commit()

            return redirect(url_for('events'))

    return render_template('event_form.html', form=form, form_name="New event", action="new_event",
                           friends=result_request)


if __name__ == "__main__":
    app.debug = True
    app.run()
