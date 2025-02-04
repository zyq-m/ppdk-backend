from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

from model import db, PPDK

bp = Blueprint("ppdk", __name__, url_prefix="/ppdk")
api = Api(bp)

ppdkParser = reqparse.RequestParser()
ppdkParser.add_argument("nama", type=str, required=True)
ppdkParser.add_argument("alamat", type=str, required=True)

ppdkFields = {
    "id": fields.String,
    "nama": fields.String,
    "negeri": fields.String,
    "alamat": fields.String,
    "admins": fields.List(
        fields.Nested(
            {
                "id": fields.String,
                "nama": fields.String,
                "email": fields.String,
                "jawatan": fields.String,
            }
        )
    ),
    "no_tel": fields.Nested({"no_tel": fields.String}),
}


class PPDKList(Resource):
    @marshal_with(ppdkFields)
    def get(self):
        ppdk = PPDK.query.all()
        return ppdk, 200

    @marshal_with(ppdkFields)
    def post(self):
        args = ppdkParser.parse_args()
        ppdk = PPDK(nama=args["nama"], alamat=args["alamat"])

        db.session.add(ppdk)
        db.session.commit()

        return ppdk, 201


api.add_resource(PPDKList, "")
