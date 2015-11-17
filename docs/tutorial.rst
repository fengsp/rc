.. _tutorial:

Tutorial
========

In this tutorial, we will create a simple blog application.  You can learn
to cache with rc and Python here.  In our blog application, anyone can add or
update a post, view all posts.


Create Skeleton
---------------

For this simple web application, we choose to use `Flask`_.  Here is the basic
skeleton::

    # -*- coding: utf-8 -*-
    import time

    from flask import Flask
    from flask import request, url_for, redirect, abort, render_template_string
    from flask_sqlalchemy import SQLAlchemy
    from rc import Cache


    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db = SQLAlchemy(app)
    cache = Cache()


    def init_db():
        db.create_all()


    if __name__ == '__main__':
        init_db()
        app.run()

.. _Flask: http://flask.pocoo.org/


Create Models
-------------

Let's declare the models and create the database schema here::

    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        content = db.Column(db.Text, nullable=False)
        created_ts = db.Column(db.Integer, nullable=False)
        updated_ts = db.Column(db.Integer, nullable=False)

        def __init__(self, title, content, created_ts, updated_ts):
            self.title = title
            self.content = content
            self.created_ts = created_ts
            self.updated_ts = updated_ts

        def __repr__(self):
            return '<Post %s>' % self.id

        @staticmethod
        def add(title, content):
            current_ts = int(time.time())
            post = Post(title, content, current_ts, current_ts)
            db.session.add(post)
            db.session.commit()
            cache.invalidate(Post.get_by_id, post.id)
            cache.invalidate(Post.get_all_ids)

        @staticmethod
        def update(post_id, title, content):
            post = Post.query.get(post_id)
            post.title = title
            post.content = content
            post.updated_ts = int(time.time())
            db.session.commit()
            cache.invalidate(Post.get_by_id, post.id)

        @staticmethod
        @cache.cache()
        def get_all_ids():
            posts = Post.query.all()
            return [post.id for post in posts]

        @staticmethod
        @cache.cache()
        def get_by_id(post_id):
            post = Post.query.get(post_id)
            return dict(id=post.id, title=post.title, content=post.content,
                        created_ts=post.created_ts, updated_ts=post.updated_ts)


View Functions
--------------

We will have four view functions here, they are used to add or update or view
a single post, view all posts.  The code explains itself::

    @app.route('/add', methods=['POST'])
    def add_post():
        title = request.form['title']
        content = request.form['content']
        Post.add(title, content)
        return redirect(url_for('show_all_posts'))


    @app.route('/post/<int:post_id>')
    def show_post(post_id):
        post = Post.get_by_id(post_id)
        if post is None:
            abort(404)
        return render_template_string(SHOW_POST_TEMPLATE, post=post)


    @app.route('/post/<int:post_id>', methods=['POST'])
    def edit_post(post_id):
        post = Post.get_by_id(post_id)
        if post is None:
            abort(404)
        title = request.form['title']
        content = request.form['content']
        Post.update(post_id, title, content)
        return redirect(url_for('show_all_posts'))


    @app.route('/')
    def show_all_posts():
        all_post_ids = Post.get_all_ids()
        all_posts = []
        with cache.batch_mode():
            for post_id in all_post_ids:
                all_posts.append(Post.get_by_id(post_id))
        all_posts = [p.value for p in all_posts]
        return render_template_string(ALL_POSTS_TEMPLATE, all_posts=all_posts)


Add The Templates
-----------------

The template for showing all posts is here.

.. sourcecode:: html+jinja

    <!DOCTYPE html>
    <html>
      <head>
        <title>Blog</title>
      </head>
      <body>
        <h1>Blog</h1>
        <form action="{{ url_for('add_post') }}" method=post>
          <dl>
            <dt>Title:
            <dd><input type=text size=50 name=title>
            <dt>Content:
            <dd><textarea name=content rows=5 cols=40></textarea>
            <dd><input type=submit value=Post>
          </dl>
        </form>
        <ul>
        {% for post in all_posts %}
          <li>
            <a href="{{ url_for('show_post', post_id=post.id) }}">
              {{ post.title }}
            </a>
          </li>
        {% endfor %}
        </ul>
      </body>
    </html>

The template for showing one post is here.

.. sourcecode:: html+jinja

    <!DOCTYPE html>
    <html>
      <head>
        <title>{{ post.title }}</title>
      </head>
      <body>
        <h1>{{ post.title }}</h1>
        <p>{{ post.content }}</p>
        <form action="{{ url_for('edit_post', post_id=post.id) }}" method=post>
          <dl>
            <dt>Title:
            <dd><input type=text size=50 name=title>
            <dt>Content:
            <dd><textarea name=content rows=5 cols=40></textarea>
            <dd><input type=submit value=Update>
          </dl>
        </form>
      </body>
    </html>

If you want the full source code check out the `tutorial source`_.

.. _tutorial source:
   https://github.com/fengsp/rc/tree/master/examples/tutorial.py
