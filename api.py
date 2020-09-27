from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from service.ApiService import ApiService

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

api_service = ApiService()


class Category(Resource):

    def get(self):
        data = api_service.get_novel_categories()
        return data


class NovelList(Resource):

    def get(self, category_id=1, page_id=1):
        data = api_service.get_novel_list(category_id, page_id)
        return data


class Novel(Resource):

    def get(self, novel_id):
        data = api_service.get_novel_catalog(novel_id)
        return data


class Chapter(Resource):

    def get(self, chapter_id):

        data = api_service.get_novel_content(chapter_id)
        return data
    

class Search(Resource):

    def get(self, keyword):
        data = api_service.get_search_novel(keyword)
        return data


api.add_resource(Category, '/', '/cat')
api.add_resource(NovelList, '/cat/<int:category_id>/page/<int:page_id>')
api.add_resource(Novel, '/novel/<string:novel_id>')
api.add_resource(Chapter, '/chapter/<string:chapter_id>')
api.add_resource(Search, '/search/<string:keyword>')


if __name__ == '__main__':
    app.run(debug=True)
