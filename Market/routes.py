from Market import app
from flask import render_template, redirect, url_for, flash, request
from Market.models import Item, User
from Market.forms import RegisterForm, LoginForm, PurchaseForm, SellForm
from Market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseForm()
    selling_form = SellForm()
    if request.method == "POST":
        # Puchase item logic
        purchased_item = request.form.get(
            'purchased_item')  # purchased_item inside get came from name of the input tag inside modals page
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for Rs {p_item_object.prettier_price}",
                      'success')
            else:
                flash(f"Unfortunately, You don't have enough money to purchase", 'danger')
        # Sell ITem logic

        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You have sold {s_item_object.name} back to Market",
                      'success')
            else:
                flash(f"Something went wrong with selling ", 'danger')

        return redirect(url_for('market_page'))
    if request.method == "GET":
        owned_items = Item.query.filter_by(owner=current_user.id)
        items = Item.query.filter_by(owner=None)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items,
                               selling_form=selling_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f"Account created successfully! You are logged in as  {user_to_create.username}", 'success')

        return redirect(url_for('market_page'))
    if form.errors != {}:  # If there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', 'danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f"Success! You are logged in as: {attempted_user.username}", 'success')
            return redirect(url_for('market_page'))
        else:
            flash("Username or password is incorrect! Please try again", 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", 'info')
    return redirect(url_for('home_page'))
