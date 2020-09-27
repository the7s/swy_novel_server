from flask import Flask
from service.ApiService import ApiService
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'user1', 'abcxyz'),
    User(2, 'user2', 'abcxyz'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
jwt = JWT(app, authenticate, identity)

api_service = ApiService()


@app.route('/')
@app.route('/cat')
def get_novel_categories():
    data = api_service.get_novel_categories()
    return data


@app.route('/cat/<int:category_id>/page/<int:page_id>')
def get_novels(category_id=1, page_id=1):
    data = api_service.get_novel_list(category_id, page_id)
    return data


@app.route('/catalog/<string:novel_id>')
def get_catalog(novel_id):
    data = api_service.get_novel_catalog(novel_id)
    return data


@app.route('/chapter/<string:chapter_id>')
def chapter(chapter_id):
    data = api_service.get_novel_content(chapter_id)
    return data


@app.route('/search/<string:keyword>')
def search(keyword):
    data = api_service.get_search_novel(keyword)
    return data


if __name__ == '__main__':
    app.run()
