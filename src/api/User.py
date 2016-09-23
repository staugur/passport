# -*- coding: utf8 -*-

__doc__ = "User login or registry rule map"

from flask import Blueprint, request
from flask_restful import Api, Resource


class User(Resource):

    """Define /user, check login, registry, list user and so on"""

    def get(self):
        return {"username": "Mr.tao"}

    def post(self):
        pass

user_blueprint = Blueprint("User", __name__)
api = Api(user_blueprint)
api.add_resource(Registry, '/user', '/user/', endpoint='user')
