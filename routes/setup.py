from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_jwt_extended import get_jwt_identity, jwt_required

from model import db, Soalan, KategoriOKU, SoalanConfig

bp = Blueprint("setup", __name__, url_prefix="/setup")
api = Api(bp)


okuParser = reqparse.RequestParser()
okuParser.add_argument("kategori", type=list, required=True)

okuFields = {
    "id": fields.String,
    "kategori": fields.String,
    "minUmur": fields.Integer(attribute="min_umur"),
    "maxUmur": fields.Integer(attribute="max_umur"),
    "skor": fields.List(fields.List(fields.Integer)),
    "kriteria": fields.Nested(
        {
            "id": fields.String,
            "kriteria": fields.String,
            "purataSkor": fields.List(
                fields.List(fields.Integer), attribute="purata_skor"
            ),
        },
        attribute="kriteria_list",
    ),
}

soalanParser = reqparse.RequestParser()
soalanParser.add_argument("soalan", type=str, required=True)

soalanFields = {
    "id": fields.String,
    "soalan": fields.String,
    "skor": fields.String,
}


class SetupOKU(Resource):
    @jwt_required()
    @marshal_with(okuFields)
    def get(self):
        oku = KategoriOKU.query.all()
        return oku

    @jwt_required()
    def post(self):
        args = request.json
        kriteria_list = [
            SoalanConfig(
                kriteria=kr.get("kriteria"),
                purata_skor=[
                    [int(min), int(max)]
                    for min, max in (
                        num.split("-") for num in kr.get("purataSkor").split(",")
                    )
                ],
            )
            for kr in args.get("kriteria")
        ]

        oku = KategoriOKU(
            kategori=args.get("kategori"),
            min_umur=args.get("minUmur"),
            max_umur=args.get("maxUmur"),
            skor=[
                [int(min), int(max)]
                for min, max in (
                    num.split("-") for num in args.get("skorKeseluruhan").split(",")
                )
            ],
            kriteria_list=kriteria_list,
        )

        db.session.add(oku)
        db.session.commit()

        return {"message": "Kategori berjaya didaftarkan"}, 201


extendedSoalan = {
    **okuFields,
    "listKriteria": fields.Nested(
        {
            "id": fields.String,
            "kriteria": fields.String,
            "soalan": fields.Nested(soalanFields, attribute="soalan", default=None),
        },
        attribute="kriteria_list",
    ),
}


class SetupSoalan(Resource):
    @jwt_required()
    @marshal_with(extendedSoalan)
    def get(self, id):
        kategori = KategoriOKU.query.filter_by(id=id).first_or_404()
        return kategori

    @jwt_required()
    def post(self, id):
        args = request.json
        kategori = KategoriOKU.query.filter_by(id=id).first_or_404()

        for k in args.get("listKriteria"):
            kriteria = SoalanConfig.query.filter_by(id=k.get("kriteria")).first_or_404(
                "Kriteria tidak wujud"
            )
            for s in k.get("soalan"):
                soalan = Soalan.query.filter_by(
                    id=s.get("sId"), kategori_oku=kategori, soalan_conf=kriteria
                ).first()
                if soalan:
                    soalan.soalan = s.get("soalan")
                    soalan.skor = s.get("skor")
                    soalan.soalan_conf = kriteria
                else:
                    new_soalan = Soalan(
                        soalan=s.get("soalan"),
                        skor=s.get("skor"),
                        kategori_oku=kategori,
                        soalan_conf=kriteria,
                    )
                    db.session.add(new_soalan)

        db.session.commit()

        return {"message": "Berjaya disimpan"}, 200

    @jwt_required()
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
