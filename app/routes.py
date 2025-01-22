# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User,Uzivatele,Produkt

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired

class FormFormular(FlaskForm):
    name = StringField('Name', validators=[ InputRequired(message="You can't leave this empty")])
    surename = StringField('Surename', validators=[ InputRequired(message="You can't leave this empty")])

@bp.route("/formular", methods=["GET", "POST"])
def formular():
    form=FormFormular()
    if form.validate_on_submit():
        print(form.name.data)
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.add(new_user)
        db.commit()
        return "Formular submitted"
    return render_template("formular.html",form=form)
# Request management
@bp.before_app_request
def before_request():
    db()

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()
    
class EditProductForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="You can't leave this empty")])
    date_added = DateField('Date Added', validators=[InputRequired(message="You can't leave this empty")])

@bp.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Produkt.query.filter_by(id=product_id).first()
    form = EditProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.date_added = form.date_added.data
        db.commit()
        return "Product updated"
    return render_template("edit_product.html", form=form, product=product)
    

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(message="You can't leave this empty")])
   

@bp.route("/add_product", methods=["GET", "POST"])
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        new_product = Produkt( name=form.name.data)
        db.add(new_product)
        db.commit()
        return "Product added"
    return render_template("product.html", form=form)

@bp.route("/list_products", methods=["GET"  ])
def list_products():
    products = Produkt.query.all()
    return render_template("list_products.html", products=products)

@bp.route("/delete_product/<int:product_id>", methods=["GET", "POST"])
def delete_product(product_id):
    product = Produkt.query.filter_by(id=product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return "Product deleted"
    return "Product not found"

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)


