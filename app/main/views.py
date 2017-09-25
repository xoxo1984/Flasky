# -*- coding: utf-8 -*-

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..decorators import permission_required
from ..models import User, Permission, Post, Follow
from flask import render_template, flash, redirect, url_for, request, current_app, abort, make_response
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
    photos = UploadSet('photos', IMAGES)
    configure_uploads(current_app, photos)
    patch_request_class(current_app)

    if form.validate_on_submit():
        if form.photo.data is not None:
            form.photos.save(form.photo.data, name=str(current_user.id) + '_temp.')
            import sys
            from config import basedir
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                avatar_path = basedir + '\\app\\static\\avatar\\'
            else:
                avatar_path = basedir + '/app/static/avatar/'
            # delete old avatar if it exists
            import os
            try:
                os.remove(avatar_path + current_user.avatar_path)
            except:
                pass
            # rename temp avatar
            temp_avatar = avatar_path + str(current_user.id) + '_temp.' + form.photo.data.filename[-3:]
            avatar = avatar_path + str(current_user.id) + '.' + form.photo.data.filename[-3:]
            os.rename(temp_avatar, avatar)

            avatar_path = str(current_user.id) + '.' + form.photo.data.filename[-3:]
            current_user.avatar_path = avatar_path

        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)

        flash('your profile has been updated')

        resp = make_response(redirect(url_for('.user', username=current_user.username)), 302)
        resp.headers['Cache-Control'] = 'max-age=0'
        return resp

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    page = request.args.get('page', 1, type=int)

    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query_result = current_user.followed_posts
    else:
        query_result = Post.query
    pagination = query_result.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config[
        'FLASKY_POST_PER_PAGE'], error_out=False)
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = pagination.items

    return render_template('index.html', form=form, posts=posts, pagination=pagination, show_followed=show_followed)


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash("You're already following this user")
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash("now you're following this user")
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash("You cannot unfollow a user which you're not following")
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash("now you're unfollowing this user")
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of", endpoint='.followers',
                           pagination=pagination, follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by", endpoint='.followed_by',
                           pagination=pagination, follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning('Flow query: %s\nParameters:%s\nDuration:%fs\nContext:%s\n' % (
                query.statement, query.parameters, query.duration, query.context))
    return response
