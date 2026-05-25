from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db, limiter
from app.forms.user_forms import ProfileForm, ChangePasswordForm, AddressForm
from app.models.user import Address
from app.models.wishlist import Wishlist
from app.models.product import Product

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name = form.last_name.data.strip()
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('user/change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/change_password.html', form=form)


@user_bp.route('/addresses')
@login_required
def addresses():
    addrs = current_user.addresses.order_by(Address.is_default.desc()).all()
    return render_template('user/addresses.html', addresses=addrs)


@user_bp.route('/addresses/add', methods=['GET', 'POST'])
@login_required
def add_address():
    form = AddressForm()
    if form.validate_on_submit():
        # If setting as default, unset others
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id).update({'is_default': False})

        addr = Address(
            user_id=current_user.id,
            full_name=form.full_name.data,
            phone=form.phone.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            is_default=form.is_default.data,
        )
        db.session.add(addr)
        db.session.commit()
        flash('Address added.', 'success')
        return redirect(url_for('user.addresses'))
    return render_template('user/address_form.html', form=form, title='Add Address')


@user_bp.route('/addresses/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    addr = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    form = AddressForm(obj=addr)
    if form.validate_on_submit():
        if form.is_default.data:
            Address.query.filter_by(user_id=current_user.id).update({'is_default': False})

        form.populate_obj(addr)
        db.session.commit()
        flash('Address updated.', 'success')
        return redirect(url_for('user.addresses'))
    return render_template('user/address_form.html', form=form, title='Edit Address')


@user_bp.route('/addresses/delete/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    addr = Address.query.filter_by(id=address_id, user_id=current_user.id).first_or_404()
    db.session.delete(addr)
    db.session.commit()
    flash('Address deleted.', 'info')
    return redirect(url_for('user.addresses'))


@user_bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.query.filter_by(user_id=current_user.id).order_by(
        Wishlist.created_at.desc()
    ).all()
    return render_template('user/wishlist.html', wishlist_items=items)


@user_bp.route('/wishlist/toggle/<int:product_id>', methods=['POST'])
@login_required
@limiter.limit("30 per minute")
def toggle_wishlist(product_id):
    product = Product.query.get_or_404(product_id)
    existing = Wishlist.query.filter_by(
        user_id=current_user.id, product_id=product_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from wishlist'})
    else:
        item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(item)
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Added to wishlist'})
