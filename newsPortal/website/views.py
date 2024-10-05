from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import desc
from .models import Post, User, Comment, Role, Permission
from .decortators import permission_required
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@permission_required('view-posts')
@login_required
def home():
    posts = Post.query.order_by(desc(Post.date_created)).all()
    return render_template("index.html", user=current_user, posts=posts)

@views.route("/create_post", methods=['GET', 'POST'])
@permission_required('create-post')
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        print(f"Required permission: {current_user.role.permission}")
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
@permission_required('delete-post')
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
@permission_required('view-posts')
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
        permissions = request.form.getlist('permission')
        if not role_name:
            flash('Role name cannot be empty', category='error')
        elif not permissions:
            flash('Permissions cannot be empty or invalid', category='error')
        else:
            role = Role(role_name=role_name)
            db.session.add(role)
            db.session.commit()
            print(role.id)
            permissions_data = [{'permission': perm, 'role_id': role.id} for perm in permissions]
            db.session.bulk_insert_mappings(Permission, permissions_data)
            db.session.commit()
            flash('Role and permissions created!', category='success')
            return redirect(url_for('views.admin'))

    return render_template("newRole.html", user=current_user)


@views.route("/view_users", methods=['GET', 'POST'])
@login_required
def list():
    users = User.query.all()
    user_count = len(users)
    return render_template("user.html",user=current_user, users=users, user_count=user_count)

@views.route("/update/<int:user_id>", methods=['GET', 'POST'])
@login_required
def update(user_id):
    user = User.query.get(user_id)
    roles = Role.query.all()

    if request.method == 'POST':
        new_role_id = request.form.get('role_id')
        
        if new_role_id:
            user.role_id = new_role_id
            db.session.commit()
            flash("Data Updated Successfully", "success")
        
        return redirect(url_for('views.list', user_id=user_id))

    return render_template("edit.html", user=user, roles=roles)