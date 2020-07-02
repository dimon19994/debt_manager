# TODO add username
# TODO уникальность почты
# TODO уникальночсть ника


from flask import Flask, render_template, redirect, url_for, request

from sqlalchemy import or_, and_
from flask_security import SQLAlchemyUserDatastore, Security, login_required, current_user
from flask_security.decorators import roles_accepted
from flask_security.utils import hash_password
from sqlalchemy.sql import func

from forms.person_form import PersonForm
from forms.event_form import EventForm
from forms.check_form import CheckForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1998@localhost/debt_manager'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = 'key'

app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'sha256_crypt'
app.config['USER_EMAIL_SENDER_EMAIL'] = "noreply@example.com"

from dao.model import *

user_datastore = SQLAlchemyUserDatastore(db, OrmUser, OrmRole)
security = Security(app, user_datastore)


@app.route('/new')
# @roles_accepted("Admin")
def new():
    role_user = OrmRole(name="User")
    role_admin = OrmRole(name="Admin")
    db.session.add_all([role_user, role_admin])
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/', methods=['GET', 'POST'])
# @roles_accepted("User")
def root():
    # return redirect(url_for('security.login'))
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
    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_f == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    except_all = all_0.except_(all_1).with_entities("col_1")
    result_friends = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()

    return render_template('friends.html', persons=result_request, friends=result_friends)


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    person_id = request.form['person_id']

    dell = Orm_Friend.delete().where(or_(and_(Orm_Friend.c.id_o == current_user.id, Orm_Friend.c.id_f == person_id),
                                         and_(Orm_Friend.c.id_f == current_user.id, Orm_Friend.c.id_o == person_id)))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/except_friend', methods=['POST'])
@login_required
def except_friend():
    person_id = request.form['person_id']

    insert = Orm_Friend.insert().values(id_o=current_user.id, id_f=person_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/deny_friend', methods=['POST'])
@login_required
def deny_friend():
    person_id = request.form['person_id']

    dell = Orm_Friend.delete().where(and_(Orm_Friend.c.id_f == current_user.id, Orm_Friend.c.id_o == person_id))

    db.session.execute(dell)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/add_fiend', methods=['POST'])
@login_required
def add_fiend():
    person_id = request.form.get('username')

    frienf_id = db.session.query(OrmUser.id).filter(OrmUser.username == person_id).one()

    insert = Orm_Friend.insert().values(id_o=current_user.id, id_f=frienf_id)

    db.session.execute(insert)
    db.session.commit()

    return redirect(url_for('friends'))


@app.route('/events', methods=['GET'])
@login_required
def events():
    result = db.session.query(OrmEvent).join(OrmParticipant).filter(
        and_(OrmEvent.id == OrmParticipant.c.event_id, OrmParticipant.c.person_di == current_user.id)).all()

    return render_template('event.html', events=result)


@app.route('/detail_event', methods=['GET', 'POST'])
@login_required
def detail_event():
    events_id = request.args.get('event_id')

    participant_id = \
        db.session.query(OrmUser.id, OrmUser.name). \
            join(OrmParticipant).filter(OrmParticipant.c.person_di == OrmUser.id). \
            join(OrmEvent).filter(OrmEvent.id == OrmParticipant.c.event_id).all()

    pay_info = \
        db.session.query(func.coalesce(func.sum(OrmPay.sum), 0), OrmParticipant.c.person_di). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
            join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
            outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_di, OrmCheck.event_id == events_id,
                                   OrmParticipant.c.person_di == OrmPay.person_id)). \
            group_by(OrmParticipant.c.person_di).order_by(OrmParticipant.c.person_di).all()

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

    if len(categories) > 0:
        return render_template('event_table.html', people=participant_id, pay=pay_info, debt=categorical_debt,
                               categories=categories, all_debts=all_debt)
    else:
        return render_template('event_table_none.html')


@app.route('/new_event', methods=['GET', 'POST'])
def new_event():
    form = EventForm()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()
    form.event_friends.choices = [(g.id, g.name + " " + g.surname) for g in result_request]

    if request.method == 'POST':
        if not form.validate():
            return render_template('event_form.html', form=form, form_name="New event", action="new_event")
        else:
            new_event = OrmEvent(
                name=form.event_name.data,
                place=form.event_place.data,
                date=form.event_date.data
            )

            add_event = db.session.query(OrmUser).filter(OrmUser.id.in_(form.event_friends.raw_data)).all()
            me = db.session.query(OrmUser).filter(OrmUser.id == current_user.id).one()
            add_event.append(me)

            for i in add_event:
                i.event.append(new_event)
                db.session.add(i)

            db.session.commit()
            return redirect(url_for('events'))

    return render_template('event_form.html', form=form, form_name="New event", action="new_event")


@app.route('/edit_event', methods=['GET', 'POST'])
@login_required
def edit_event():
    form = EventForm()

    all_0 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2")).filter(
        Orm_Friend.c.id_o == current_user.id)
    all_1 = db.session.query(Orm_Friend.c.id_o.label("col_1"), Orm_Friend.c.id_f.label("col_2"))
    all_2 = db.session.query(Orm_Friend.c.id_f.label("col_1"), Orm_Friend.c.id_o.label("col_2"))
    except_all = all_0.except_(all_1.except_(all_2)).with_entities("col_2")
    result_request = db.session.query(OrmUser).filter(OrmUser.id.in_(except_all)).all()
    form.event_friends.choices = [(g.id, g.name + " " + g.surname) for g in result_request]

    if request.method == 'GET':

        event_id = request.args.get('event_id')
        event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()

        form.event_id.data = event_id
        form.event_name.data = event.name
        form.event_place.data = event.place
        form.event_date.data = event.date

        return render_template('event_form.html', form=form, form_name="Edit event", action="edit_event")


    else:

        if not form.validate():
            return render_template('event_form.html', form=form, form_name="Edit event", action="edit_event")
        else:
            event = db.session.query(OrmEvent).filter(OrmEvent.id == form.event_id.data).one()

            event.name = form.event_name.data,
            event.place = form.event_place.data,
            event.date = form.event_date.data

            participates = db.session.query(OrmUser). \
                join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
                join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
                filter(OrmEvent.id == form.event_id.data)

            add_event = db.session.query(OrmUser).filter(OrmUser.id.in_(form.event_friends.raw_data))
            me = db.session.query(OrmUser).filter(OrmUser.id == current_user.id)

            to_del = participates.except_(add_event.union(me)).all()

            to_add = add_event.union(me).except_(participates).all()

            for i in to_del:
                i.event.remove(event)
                db.session.add(i)

            for i in to_add:
                i.event.append(event)
                db.session.add(i)

            db.session.commit()

            return redirect(url_for('events'))


@app.route('/delete_event', methods=['POST'])
@login_required
def delete_event():
    event_id = request.form['event_id']
    event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()

    participates = db.session.query(OrmUser). \
        join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        filter(OrmEvent.id == event_id).all()

    for i in participates:
        i.event.remove(event)
        db.session.add(i)
    db.session.commit()

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('security.login'))


@app.route('/checks', methods=['GET'])
@login_required
def checks():
    result = db.session.query(OrmCheck.id, OrmCheck.description, OrmCheck.sum, OrmEvent.name, OrmEvent.date).\
        join(OrmEvent, OrmEvent.id == OrmCheck.event_id).\
        join(OrmParticipant, OrmParticipant.c.event_id == OrmEvent.id).\
        join(OrmUser, OrmParticipant.c.person_di == OrmUser.id).filter(OrmUser.id == current_user.id).all()

    return render_template('event.html', checks=result)


@app.route('/new_check', methods=['GET', 'POST'])
def new_check():
    form = CheckForm()

    if request.method == 'POST':
        if not form.validate():
            return render_template('check_form.html', form=form, form_name="New check", action="new_check")
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

    return render_template('check_form.html', form=form, form_name="New check", action="new_check")



if __name__ == "__main__":
    app.debug = True
    app.run()
