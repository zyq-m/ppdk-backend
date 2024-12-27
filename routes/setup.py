from flask import Blueprint, request, json
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_jwt_extended import get_jwt_identity, jwt_required

from model import db, Soalan, KategoriOKU

bp = Blueprint("setup", __name__, url_prefix="/setup")
api = Api(bp)


okuParser = reqparse.RequestParser()
okuParser.add_argument("kategori", type=list, required=True)

okuFields = {
    "id": fields.String,
    "kategori": fields.String,
}

soalanParser = reqparse.RequestParser()
soalanParser.add_argument("soalan", type=str, required=True)

soalanFields = {
    "id": fields.String,
    "soalan": fields.String,
    "kategori_oku": fields.Nested(okuFields),
    "created_at": fields.DateTime,
}


class SetupOKU(Resource):
    @marshal_with(okuFields)
    def get(self):
        oku = KategoriOKU.query.all()
        return oku

    def post(self):
        args = json.loads(request.data)
        oku = list(
            map(lambda oku: KategoriOKU(kategori=oku["kategori"]), args["kategori"])
        )

        db.session.add_all(oku)
        db.session.commit()

        return {"message": "Berjaya didaftarkan"}, 201


class SetupSoalan(Resource):
    @marshal_with(soalanFields)
    def get(self, id):
        soalan = Soalan.query.filter_by(kategori_id=id).all()
        return soalan

    def post(self, id):
        args = json.loads(request.data)

        for s in args["soalan"]:
            soalan = Soalan.query.filter_by(id=s["id"], kategori_id=id).first()
            if soalan:
                soalan.soalan = s["soalan"]
            else:
                new_soalan = Soalan(soalan=s["soalan"], kategori_id=id)
                db.session.add(new_soalan)

        db.session.commit()

        return {"message": "Berjaya dikemaskini"}, 200

    def delete(self, id):
        soalan = Soalan.query.filter_by(id=id).first()
        if soalan:
            db.session.delete(soalan)
            db.session.commit()
            return {"message": "Berjaya dipadam"}, 200
        else:
            return {"message": "Soalan tidak wujud"}, 404


api.add_resource(SetupOKU, "/oku")
api.add_resource(SetupSoalan, "/soalan/<int:id>")
