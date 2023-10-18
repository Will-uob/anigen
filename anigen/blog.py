from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from anigen.auth import login_required
from anigen.db import get_db

""" Json and requests look like really useful libraries to learn desu"""
import json
import requests

API_URL = "https://api-inference.huggingface.co/models/hakurei/waifu-diffusion"
API_TOKEN = ""
headers = {"Authorization": f"Bearer {API_TOKEN}"}

from uuid import uuid4
import os

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.content

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, seed, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        seed = request.form['seed']
        prompt = request.form['prompt']
        error = None

        if not title:
            error = 'Title is required.'

        image = query({
	        "inputs": prompt,
        })

        path = f"static/images/{g.user['id']}"
        os.mkdir(path)

        ident = uuid4().__str__()
        path = f"images/{g.user['id']}/ani_{ident}.png"
        image.save(path)

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, seed, prompt, filepath, author_id)'
                # (title, seed, prompt, path, g.user['id'])
                ' VALUES (?, ?, ?, ?, ?)',
                (title, seed, prompt, "hello", g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, seed, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # SELECT p.id, title, seed, created, author_id, username, filepath

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        seed = request.form['seed']
        prompt = request.form['prompt']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, seed = ?, prompt = ?'
                ' WHERE id = ?',
                (title, seed, prompt, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # post = get_post(id)
    get_post(id)
    # os.remove(post[-1]) -> Removes the image from directory, before we delete the post!
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

"""
Legacy stuffs
        This code will be tested on the lab machine tomorrow!
        pipe = StableDiffusionPipeline.from_pretrained(
        'hakurei/waifu-diffusion',
        torch_dtype=torch.float32
        ).to('cuda')

        with autocast("cuda"):
             image = pipe(prompt, guidance_scale=6)[0][0]

        https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask

        path = f"static/images/{g.user['id']}"
        os.mkdir(path)

        ident = uuid4().__str__()
        path = f"images/{g.user['id']}/ani_{ident}.png"
        image.save(path)
"""