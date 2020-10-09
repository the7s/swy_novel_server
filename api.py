from flask import Flask
from service.ApiService import ApiService
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from flask_restful import reqparse


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'user1', 'password1'),
    User(2, 'user2', 'password2'),
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


# @app.route('/novels/<int:category_id>/page/<int:page_id>')
@app.route('/novels')
def get_novels():
    parser = reqparse.RequestParser()
    parser.add_argument('category_id', type=int, help='category_id cannot be converted')
    parser.add_argument('page', type=int, help='page cannot be converted')
    args = parser.parse_args()
    category_id = args['category_id'] if args['category_id'] is not None else 1
    page = args['page'] if args['page'] is not None else 1
    data = api_service.get_novel_list(category_id, page)
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
