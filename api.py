from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from service.ApiService import ApiService

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('task')

api_service = ApiService()


class Category(Resource):

    def get(self):
        data = api_service.get_novel_categories()
        return data


class NovelList(Resource):

    def get(self, category_id=1, page_id=1):
        data = api_service.get_novel_list(category_id, page_id)
        return data
        pass


class Novel(Resource):

    def get(self,novel_id):
        data = api_service.get_novel(novel_id)
        return data
        pass


api.add_resource(Category, '/cat')
api.add_resource(NovelList, '/cat/<int:category_id>/page/<int:page_id>')
api.add_resource(Novel, '/novel/<string:novel_id>')


if __name__ == '__main__':
    app.run(debug=True)
