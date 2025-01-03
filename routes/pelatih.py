import ast
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.score import ScoreCalculator
from utils.umur import UmurCalculator

from model import db, Admin, Phone, Pelatih, Penjaga

bp = Blueprint("pelatih", __name__, url_prefix="/pelatih")
api = Api(bp)

pelatihParser = reqparse.RequestParser()
pelatihParser.add_argument("no_kp", type=str, required=True)
pelatihParser.add_argument("nama", type=str, required=True)
pelatihParser.add_argument("kaum", type=str, required=True)
pelatihParser.add_argument("jantina_id", type=str, required=True)
pelatihParser.add_argument("alamat", type=str, required=True)
pelatihParser.add_argument("negeri", type=str, required=True)
pelatihParser.add_argument("nama_penjaga", type=str, required=True)
pelatihParser.add_argument("hubungan", type=str, required=True)
pelatihParser.add_argument("alamat_penjaga", type=str, required=True)
pelatihParser.add_argument("no_tel", type=str, required=True)

pelatihFields = {
    "id": fields.String,
    "nama": fields.String,
    "no_kp": fields.String,
    "kaum": fields.String,
    "umur": fields.Integer,
    "jantina": fields.Nested(
        {
            "id": fields.String,
            "jantina": fields.String,
        }
    ),
    "alamat": fields.String,
    "negeri": fields.String,
    "role": fields.Nested(
        {
            "id": fields.String,
            "name": fields.String,
        }
    ),
    "admin_ppdk": fields.Nested(
        {
            "id": fields.String,
            "nama": fields.String,
            "email": fields.String,
            "ppdk": fields.Nested(
                {
                    "id": fields.String,
                    "nama": fields.String,
                }
            ),
        }
    ),
    "penjaga": fields.List(
        fields.Nested(
            {
                "id": fields.String,
                "nama": fields.String,
                "hubungan": fields.String,
                "alamat": fields.String,
                "no_tel": fields.List(
                    fields.Nested(
                        {
                            "id": fields.String,
                            "no_tel": fields.String,
                        }
                    )
                ),
            }
        )
    ),
    "assessment": fields.List(
        fields.Nested(
            {
                "id": fields.String,
                "kategori_oku": fields.Nested(
                    {
                        "id": fields.String,
                        "kategori": fields.String,
                    }
                ),
                "skor": fields.Integer,
                "indicator": fields.String,
                "created_at": fields.String,
            }
        )
    ),
}


class ListPelatih(Resource):
    @marshal_with(pelatihFields)
    @jwt_required()
    def get(self):
        payload = ast.literal_eval(get_jwt_identity())
        admin_ppdk = Admin.query.filter_by(email=payload["email"]).first_or_404()
        pelatih = Pelatih.query.filter_by(admin_ppdk=admin_ppdk).all()

        for p in pelatih:
            umur = UmurCalculator(p.no_kp)
            p.umur = umur.get_age()

        return pelatih, 200

    # @marshal_with(pelatihFields)
    @jwt_required()
    def post(self):
        args = pelatihParser.parse_args()
        payload = ast.literal_eval(get_jwt_identity())
        admin_ppdk = Admin.query.filter_by(email=payload["email"]).first_or_404()

        new_pelatih = Pelatih(
            nama=args["nama"],
            no_kp=args["no_kp"],
            kaum=args["kaum"],
            alamat=args["alamat"],
            negeri=args["negeri"],
            jantina_id=args["jantina_id"],
            daftar_oleh=admin_ppdk.id,
        )

        new_penjaga = Penjaga(
            nama=args["nama_penjaga"],
            hubungan=args["hubungan"],
            alamat=args["alamat_penjaga"],
            pelatih=new_pelatih,
        )
        no_tel = Phone(no_tel=args["no_tel"], penjaga=new_penjaga)

        db.session.add_all([new_pelatih, new_penjaga, no_tel])
        db.session.commit()

        return {"message": "Berjaya didaftarkan"}, 201


class PelatihInfo(Resource):
    @marshal_with(pelatihFields)
    def get(self, id):
        pelatih = Pelatih.query.filter_by(id=id).first_or_404()

        for p in pelatih.assessment:
            jawapan = ast.literal_eval(p.jawapan)
            score = ScoreCalculator(jawapan)
            p.indicator = score.classify_score()

        umur = UmurCalculator(pelatih.no_kp)
        pelatih.umur = umur.get_age()
        return pelatih, 200

    def put(self, id):
        args = pelatihParser.parse_args()
        pelatih = Pelatih.query.filter_by(id=id).first_or_404()
        pelatih.nama = args["nama"]
        pelatih.no_kp = args["no_kp"]
        pelatih.kaum = args["kaum"]
        pelatih.jantina_id = args["jantina_id"]
        pelatih.alamat = args["alamat"]
        pelatih.negeri = args["negeri"]
        pelatih.penjaga[0].nama = args["nama_penjaga"]
        pelatih.penjaga[0].hubungan = args["hubungan"]
        pelatih.penjaga[0].alamat = args["alamat_penjaga"]

        db.session.commit()

        return {"message": "Berjaya kemas kini"}, 200


api.add_resource(ListPelatih, "/")
api.add_resource(PelatihInfo, "/<int:id>")
