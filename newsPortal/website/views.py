from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from .models import Post, User, Comment, Role
from . import db
import uuid

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.order_by(desc(Post.date_created)).all()
    return render_template("home.html", user=current_user, posts=posts)

@views.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        # img = str(uuid.uuid4())
        # image = request.files.get('image')
        # image_filename = 'images/' + img + '.jpg'
        # image.save('images/' + img + '.jpg')
        # print(image_filename)

        if not text:
            flash('Text & Images cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("create_post.html", user=current_user)

@views.route("/delete/<id>")
@login_required
def delete(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    return redirect(url_for('views.home'))

@views.route("/posts/<name>")
@login_required
def posts(name):
    user = User.query.filter_by(name=name).first()

    if not user:
        flash('No  User exists.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=user.id).all()
    return render_template("posts.html", user=current_user, posts=posts, name=name)

@views.route("/comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

@views.route("/admin-panel")
@login_required
def admin():
    return render_template("admin.html", user=current_user)

@views.route("/new_role", methods=['GET', 'POST'])
@login_required
def new_role():
    if request.method == "POST":
        role_name = request.form.get('role')
        permisson = request.form.get('permisson')

        if not role_name:
            flash('Role name cannot be empty', category='error')
        elif not permisson == "Select permissions":
            flash('Permissions cannot be empty or invalid', category='error')
        else:
            role = Role(role_name=role_name, permisson=permisson)
            db.session.add(role)
            db.session.commit()
            flash('Role created!', category='success')
            return redirect(url_for('views.admin'))
        
    return render_template("newRole.html", user=current_user) 