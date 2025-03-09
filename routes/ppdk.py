from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

from model import db, PPDK, Phone

bp = Blueprint("ppdk", __name__, url_prefix="/ppdk")
api = Api(bp)

ppdkParser = reqparse.RequestParser()
ppdkParser.add_argument("nama", type=str, required=True)
ppdkParser.add_argument("notel", type=str, required=True)
ppdkParser.add_argument("negeri", type=str, required=True)
ppdkParser.add_argument("alamat", type=str, required=True)
ppdkParser.add_argument("active", type=bool, required=False)

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
        ppdk = PPDK.query.filter(PPDK.active).all()
        return ppdk, 200

    def post(self):
        args = ppdkParser.parse_args()
        ppdk = PPDK(nama=args["nama"],
                    alamat=args["alamat"], negeri=args["negeri"])
        notel = Phone(ppdk_lookup=ppdk, no_tel=args["notel"])

        db.session.add(ppdk)
        db.session.add(notel)
        db.session.commit()

        return {"message": "Cawangan PPDK baharu berjaya didaftarkan"}, 201


class PpdkController(Resource):
    def put(self, ppdk_id):
        ppdk = PPDK.query.get(ppdk_id)
        if not ppdk:
            return {"message": "Cawangan PPDK tidak wujud"}, 404

        args = ppdkParser.parse_args()
        ppdk.nama = args.get("nama", ppdk.nama)
        ppdk.alamat = args.get("alamat", ppdk.alamat)
        ppdk.negeri = args.get("negeri", ppdk.negeri)
        ppdk.active = args.get("active", ppdk.active)

        if "notel" in args:
            notel = Phone.query.filter_by(ppdk_lookup=ppdk).first()
            if notel:
                notel.no_tel = args["notel"]
            else:
                notel = Phone(ppdk_lookup=ppdk, no_tel=args["notel"])
                db.session.add(notel)

        db.session.commit()

        if "active" in args:
            return {"message": "Cawangan PPDK berjaya dipadam"}, 200

        return {"message": "Cawangan PPDK berjaya dikemaskini"}, 200


api.add_resource(PPDKList, "")
api.add_resource(PpdkController, "/<int:ppdk_id>")
