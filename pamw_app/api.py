from flask import Blueprint, render_template, abort, Response, jsonify
from flask_restful import Api, Resource, url_for
from flask_jwt import JWT, jwt_required, current_identity
from pamw_app.serializers import PackageSerializer, UserSerializer
import pamw_app.models as models

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

package_serializer = PackageSerializer()
packages_serializer = PackageSerializer(many=True)

user_serializer = UserSerializer()

def api_authenticate(username, password):
    return models.User.authorize(username, password, api=True)


def api_identity(payload):
    user_id = payload['identity']
    return models.User.query.get(user_id)

jwt = JWT(authentication_handler=api_authenticate, identity_handler=api_identity)

class PackageList(Resource):
    @jwt_required()
    def get(self):
        packages = models.Package.query.all()
        return packages_serializer.dump(packages)


class Package(Resource):
    @jwt_required()
    def get(self, package_id):
        package = models.Package.query.get(package_id)
        if package is None:
            return {'message': 'Package not found'}, 404
        else:
            return package_serializer.dump(package)
    
    @jwt_required()
    def patch(self, package_id):
        package = models.Package.query.get(package_id)
        if package is None:
            return {'message': 'Package not found'}, 404
        else:
            res = package.increment_status()
            if res:
                return {'message': 'Successfully set new status', 'status': package.status}, 200
            else:
                return {'message': 'Cannot increment status any further'}, 400

    def delete(self, package_id):
        package = models.Package.query.get(package_id)
        if package is None:
            return {'message': 'Package not found'}, 404
        else:
            res = package.delete()
            if res:
                return {'message': 'Package deleted'}, 200
            else:
                return {'message': 'Package cannot be deleted anymore.'}, 400


class Sender(Resource):
    @jwt_required()
    def get(self, sender_id):
        sender = models.User.query.get(sender_id)
        if sender is None or sender.user_type != 'sender':
            return {'message': 'Sender not found'}, 404
        else:
            return user_serializer.dump(sender)


class SenderPackages(Resource):
    @jwt_required()
    def get(self, sender_id):
        sender = models.User.query.get(sender_id)
        if sender is None or sender.user_type != 'sender':
            return {'message': 'Sender not found'}, 404
        else:
            packages = models.Package.query.filter_by(sender_id=sender_id)
            return packages_serializer.dump(packages)


api.add_resource(PackageList, '/packages/', endpoint='packages')
api.add_resource(Package, '/packages/<package_id>', endpoint='package_detail')
api.add_resource(Sender, '/senders/<sender_id>', endpoint='sender_detail')
api.add_resource(SenderPackages, '/senders/<sender_id>/packages', endpoint='sender_packages')
