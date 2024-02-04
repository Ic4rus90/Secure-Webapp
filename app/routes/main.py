from flask import flash, Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from app.db.boat import get_boat_by_id, get_boats, add_boat_to_db
import bleach

from app.db.review import get_boat_reviews, add_review_to_db
from app.db.user import get_user
from app.forms.auth_forms import EditUsernameForm, EditPhoneForm, EditPasswordForm
from app.forms.boat_forms import AddReviewForm, AddBoatForm
from app.models.boat import Boat
from app.models.review import Review


main_routes = Blueprint('main', __name__)


@main_routes.route('/add_boat/', methods=['GET', 'POST'])
@login_required
def add_boat():
    form = AddBoatForm()  # Instantiate your form class
    if request.method == 'POST':
        if form.validate_on_submit():  # Validates the form data
            # Create a new Boat object using the validated form data
            boat = Boat(
                type=bleach.clean(form.boat_type.data, strip=True),
                make=bleach.clean(form.make.data, strip=True),
                foot=form.length.data,
                year=form.year.data,
                engineMake=bleach.clean(form.engine_make.data, strip=True),
                engineHp=form.engine_hp.data,
                price=form.price.data,
                description=bleach.clean(form.description.data, strip=True),
                image_url=bleach.clean(form.image_url.data, strip=True)
            )
            add_boat_to_db(boat)
            flash('Boat added', 'success')
            return redirect(url_for('main.boat_screen'))  # Redirect to the boat screen view
        else:
            for fieldName, errorMessages in form.errors.items():
                for err in errorMessages:
                    flash(f"{fieldName}: {err}", 'error')
    # GET request or POST with errors: render the 'add_boat.html' template
    return render_template('add_boat.html', form=form)  # Pass form object to the template


@main_routes.route("/show_boat/", methods=['GET'])
@login_required
def show_specific_boat():
    boat_id = request.args.get('id')
    if boat_id is None:
        return redirect(url_for('404'))

    boat = get_boat_by_id(boat_id)
    reviews = get_boat_reviews(boat_id)
    form = AddReviewForm()
    return render_template("boat.html", name=current_user.username, boat=boat, reviews=reviews, form=form)


@main_routes.route("/add_review/", methods=['POST'])
@login_required
def add_review():
    form = AddReviewForm()
    boat_id = request.form.get('boat_id')

    if form.validate_on_submit():
        review = Review(
            boat_id=boat_id,
            username=current_user.username,
            stars=form.stars.data,
            content=bleach.clean(form.content.data, strip=True)
        )
        add_review_to_db(review)

        flash('Review added', 'success')
        return redirect(url_for('main.show_specific_boat', id=boat_id))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"{fieldName}: {err}", 'error')
    boat = get_boat_by_id(boat_id)
    reviews = get_boat_reviews(boat_id)
    return render_template("boat.html", name=current_user.username, boat=boat, reviews=reviews, form=form)


@main_routes.route("/profile/", methods=['GET'])
@login_required
def profile():
    user = get_user(current_user.id)
    return render_template("profile.html", user=user)


@main_routes.route("/edit_profile/", methods=['GET'])
@login_required
def edit_profile():
    username_form = EditUsernameForm()
    phone_form = EditPhoneForm()
    password_form = EditPasswordForm()
    cur_user = get_user(current_user.id)

    return render_template("edit_profile.html",
                           username_form=username_form,
                           phone_form=phone_form,
                           password_form=password_form,
                           user=cur_user)


@main_routes.route('/boats/')
def show_boats():
    boats = get_boats()
    return render_template("get_boats.html", boats=boats)


@main_routes.route("/boatscreen/", methods=['GET', 'POST'])
@login_required
def boat_screen():
    boats = get_boats()
    return render_template("boat_screen.html", boats=boats)


@main_routes.route("/", methods=['GET', 'POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.boat_screen'))
    else:
        return render_template("home.html")
