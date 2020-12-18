from flask_marshmallow import Marshmallow
from marshmallow import post_dump
from pamw_app.models import Package, User

ma = Marshmallow()


class PackageSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Package

    _links = ma.Hyperlinks(
        {
            'self': ma.URLFor("api.package_detail", values=dict(package_id="<id>")),
            'collection': ma.URLFor("api.packages"),
            'sender': ma.URLFor('api.sender_detail', values=dict(sender_id='<sender_id>')),
            'increment_status': ma.URLFor('api.package_detail', values=dict(package_id='<id>'))
        }
    )

    @post_dump()
    def postprocess(self, data, many=False):
        if data['status'] == 'Odebrana':
            del data['_links']['increment_status']
        return data


class UserSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password', )
    
    _link = ma.Hyperlinks(
        {
            'self': ma.URLFor('api.sender_detail', values=dict(sender_id='<id>')),
            'packages': ma.URLFor('api.sender_packages', values=dict(sender_id='<id>'))
        }
    )
