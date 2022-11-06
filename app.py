from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rubrics = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    q = request.args.get('q')
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    if q:
        articles = Article.query.filter(Article.text.contains(q) | Article.rubrics.contains(q) | Article.created_date.contains(q))
    else:
        articles = Article.query.order_by(Article.created_date.desc())
    pages = articles.paginate(page=page, per_page=20)

    return render_template("index.html", pages=pages)


@app.route('/post/<int:id>')
def post(id):
    article = Article.query.get(id)
    return render_template("post.html", article=article)

@app.route('/post/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/')
    except:
        return "При удалении записи произошла ошибка"


@app.route('/post/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.rubrics = request.form['rubrics']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "При редактировании поста произошла ошибка"
    else:
        return render_template("post_update.html", article=article)


@app.route('/add', methods=['POST', 'GET'])
def add_messag():
    if request.method == "POST":
        rubrics = request.form['rubrics']
        text = request.form['text']

        article = Article(rubrics=rubrics, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            return "При добовлении поста произошла ошибка"
    else:
        return render_template("addmessag.html")


if __name__ == "__main__":
    app.run(debug=True)