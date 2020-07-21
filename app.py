# TODO add username
# TODO уникальность почты
# TODO уникальночсть ника
# TODO Ник только англ


from flask import Flask, render_template, redirect, url_for, request
from flask_security import SQLAlchemyUserDatastore, Security, login_required, current_user, roles_accepted
from flask_security.utils import hash_password
from sqlalchemy import or_, and_
from sqlalchemy.sql import func

from forms.check_form import CheckForm
from forms.debt_form import DebtForm
from forms.event_form import EventForm
from forms.person_form import PersonForm
from forms.repay_form import RepayForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:01200120@localhost/debt_manager'
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
# @roles_accepted(str(current_user.id))
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
        and_(OrmEvent.id == OrmParticipant.c.event_id, OrmParticipant.c.person_di == current_user.id)).\
        order_by(OrmEvent.date.desc()).all()

    return render_template('event.html', events=result)


@app.route('/detail_event', methods=['GET', 'POST'])
@login_required
def detail_event():
    events_id = request.args.get('event_id')

    participant_id = \
        db.session.query(OrmUser.id, OrmUser.name). \
            join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id).\
            filter(OrmEvent.id == events_id).\
            order_by(OrmUser.id).all()

    pay_info = \
        db.session.query(func.coalesce(func.sum(OrmPay.sum), 0), OrmParticipant.c.person_di). \
            join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id). \
            join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
            outerjoin(OrmPay, and_(OrmCheck.id == OrmPay.check_di, OrmParticipant.c.person_di == OrmPay.person_id)). \
            filter(OrmCheck.event_id == events_id). \
            group_by(OrmParticipant.c.person_di).order_by(OrmParticipant.c.person_di).all()

    categorical_debt = \
        db.session.query(func.sum(OrmDebt.sum), OrmDebt.person_id, OrmItem.category). \
            join(OrmItem, OrmDebt.item_di == OrmItem.id). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmDebt.person_id, OrmItem.category).order_by(OrmDebt.person_id, OrmItem.category).all()

    all_debt = \
        db.session.query(func.sum(OrmDebt.sum), OrmDebt.person_id). \
            join(OrmItem, OrmDebt.item_di == OrmItem.id). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmDebt.person_id).order_by(OrmDebt.person_id).all()

    categories = \
        db.session.query(OrmItem.category). \
            join(OrmCheck, and_(OrmItem.check_id == OrmCheck.id, OrmCheck.event_id == events_id)). \
            group_by(OrmItem.category).order_by(OrmItem.category).all()

    who_repay = db.session.query(func.sum(OrmRepay.sum), OrmRepay.id_debt.label('id')). \
            filter(and_(OrmRepay.id_event == events_id, OrmRepay.active)). \
            group_by(OrmRepay.id_debt).\
            order_by(OrmRepay.id_debt).all()

    whom_repay = db.session.query(func.sum(OrmRepay.sum), OrmRepay.id_repay.label('id')). \
        filter(and_(OrmRepay.id_event == events_id, OrmRepay.active)). \
        group_by(OrmRepay.id_repay). \
        order_by(OrmRepay.id_repay).all()

    if len(categories) > 0:
        return render_template('event_table.html', people=participant_id, pay=pay_info, debt=categorical_debt,
                               categories=categories, all_debts=all_debt, id=events_id, who_repay=who_repay, whom_repay=whom_repay)
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
    result = db.session.query(OrmCheck.id, OrmCheck.description, OrmCheck.sum, OrmEvent.name, OrmEvent.date). \
        join(OrmEvent, OrmEvent.id == OrmCheck.event_id). \
        join(OrmParticipant, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmUser, OrmParticipant.c.person_di == OrmUser.id).filter(OrmUser.id == current_user.id).\
        order_by(OrmEvent.date.desc(), OrmCheck.id).all()

    return render_template('check.html', checks=result)


@app.route('/new_check', methods=['GET', 'POST'])
def new_check():
    form = CheckForm()

    event_id = request.args.get('event_id')
    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id).filter(OrmEvent.id == event_id).\
        order_by(OrmUser.id).all()
    for i in range(len(form.check_pay)):
        form.check_pay[i].choices = [(g.id, g.name + " " + g.surname) for g in people]

    if request.method == 'POST':
        if not form.validate():
            return render_template('check_form.html', form=form, form_name="New check", action="new_check", id=event_id)
        else:
            add = []

            new_check = OrmCheck(
                sum=round(sum(form.check_sum.data),2),
                description=form.check_description.data
            )

            event = db.session.query(OrmEvent).filter(OrmEvent.id == event_id).one()
            event.check.append(new_check)
            add.append(event)

            sale = form.check_sale.data/len(people)

            for i in range(len(form.check_pay.data)):
                new_check.user_pay.append(OrmPay(person_id=form.check_pay.data[i], sum=round(form.check_sum.data[i], 2)))

            for i in range(len(form.check_item.data)):
                new_check.item.append(OrmItem(
                    name=form.check_item.data[i],
                    cost=round(form.item_cost.data[i]+sale, 2),
                    category=form.item_type.data[i]
                ))

            db.session.add(event)
            db.session.commit()

            return redirect(url_for('new_debt', id=new_check.id))

    return render_template('check_form.html', form=form, form_name="New check", action="new_check", id=event_id)


@app.route('/new_debt/<id>', methods=['GET', 'POST'])
def new_debt(id):
    form = DebtForm()

    items = db.session.query(OrmItem.id, OrmItem.name, OrmItem.cost).join(OrmCheck, OrmCheck.id == OrmItem.check_id). \
        filter(OrmCheck.id == id).all()

    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
        filter(OrmCheck.id == id).order_by(OrmUser.id).all()


    if request.method == 'POST':
        for i in range(len(items)):
            if str(i) in str(form.debt_all):
                price = items[i].cost/len(people)
                for j in people:
                    deb = OrmDebt(
                        item_di=items[i].id,
                        person_id=j.id,
                        sum=round(price, 2)
                    )
                    db.session.add(deb)
                    db.session.commit()
            else:
                count = form.debt_count.data[len(people)*i:len(people)*i+len(people)]
                for j in range(len(people)):
                    if count[j]>0:
                        deb = OrmDebt(
                            item_di=items[i].id,
                            person_id=people[j].id,
                            sum=round(items[i].cost/sum(count)*count[j], 2)
                        )
                        db.session.add(deb)
                        db.session.commit()

        return redirect(url_for('checks'))

    for i in range(len(items)):
        for j in range(len(people)):
            form.debt_count.append_entry()
            # form.debt_type[-1].name = str(items[i].id) + "-" + str(people[j].id)
            # form.debt_type[-1].id = str(items[i].id) + "-" + str(people[j].id)
        form.debt_all.append_entry()
        # form.debt_type[-1].name = str(items[i].id) + "-all"
        # form.debt_type[-1].id = str(items[i].id) + "-all"
    return render_template('debt_form.html', form=form, form_name="New debt", action="new_debt", people=people,
                           items=items, id=id)


@app.route('/detail_check', methods=['GET', 'POST'])
@login_required
def detail_check():
    check_id = request.args.get('check_id')

    items = db.session.query(OrmItem).\
        join(OrmCheck, OrmCheck.id == OrmItem.check_id).\
        filter(OrmCheck.id == check_id).order_by(OrmItem.id).all()

    debt = db.session.query(OrmDebt).\
        join(OrmItem, OrmItem.id == OrmDebt.item_di).\
        filter(OrmItem.check_id == check_id).\
        order_by(OrmDebt.item_di, OrmDebt.person_id).all()

    people = db.session.query(OrmUser). \
        join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
        join(OrmEvent, OrmParticipant.c.event_id == OrmEvent.id). \
        join(OrmCheck, OrmEvent.id == OrmCheck.event_id). \
        filter(OrmCheck.id == check_id).order_by(OrmUser.id).all()

    return render_template('check_table.html', items=items, debt=debt, people=people)


@app.route('/new_repay', methods=['GET', 'POST'])
def new_repay():
    form = RepayForm()

    event_id = request.args.get('event_id')
    people = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname). \
        join(OrmParticipant, OrmParticipant.c.person_di == OrmUser.id). \
        join(OrmEvent, OrmEvent.id == OrmParticipant.c.event_id).filter(OrmEvent.id == event_id)
    me = db.session.query(OrmUser.id, OrmUser.name, OrmUser.surname).\
        filter(OrmUser.id == current_user.id)
    people = people.except_(me).order_by(OrmUser.id).all()

    form.repay_id.choices = [(g.id, g.name + " " + g.surname) for g in people]

    form.event_id.data = event_id
    form.my_id.data = current_user.id

    if request.method == 'POST':
        if not form.validate():
            return render_template('repey_form.html', form=form, form_name="New repay", action="new_repay", id=event_id)
        else:
            new_repay = OrmRepay(
                id_event=form.event_id.data,
                id_debt=form.my_id.data,
                id_repay=form.repay_id.data,
                sum=form.repay_sum.data,
                active=True
                #TODO Поменять на False и добавить отображение
            )

            db.session.add(new_repay)
            db.session.commit()

            return redirect(url_for('events'))


    return render_template('repey_form.html', form=form, form_name="New repay", action="new_repay", id=event_id)


if __name__ == "__main__":
    app.debug = True
    app.run()
