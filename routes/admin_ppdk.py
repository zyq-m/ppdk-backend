from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort

from model import db, Admin, PPDK, Phone
from extensions import f_bcrypt

bp = Blueprint("admin-ppdk", __name__, url_prefix="/admin-ppdk")
api = Api(bp)

adminParser = reqparse.RequestParser()
adminParser.add_argument("email", type=str, required=True)
adminParser.add_argument("nama", type=str, required=True)
adminParser.add_argument("no_tel", type=str, required=True)
adminParser.add_argument("jawatan", type=str, required=True)
adminParser.add_argument("password", type=str, required=True)
adminParser.add_argument("ppdk_id", type=str, required=True)

adminFields = {
    "id": fields.String,
    "nama": fields.String,
    "email": fields.String,
    "jawatan": fields.String,
    "role": fields.Nested(
        {
            "id": fields.String,
            "name": fields.String,
        }
    ),
    "ppdk": fields.Nested(
        {
            "id": fields.String,
            "nama": fields.String,
            "alamat": fields.String,
        }
    ),
    "no_tel": fields.List(
        fields.Nested(
            {
                "id": fields.String,
                "no_tel": fields.String,
            }
        )
    ),
    "pelatih_list": fields.List(
        fields.Nested(
            {
                "id": fields.String,
                "nama": fields.String,
                "no_kp": fields.String,
                "kaum": fields.String,
                "alamat": fields.String,
                "negeri": fields.String,
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
            }
        )
    ),
}


class ListAdminPPDK(Resource):
    @marshal_with(adminFields)
    def get(self):
        ppdk = Admin.query.all()
        return ppdk, 200

    @marshal_with(adminFields)
    def post(self):
        args = adminParser.parse_args()
        ppdk = PPDK.query.filter_by(id=args["ppdk_id"]).first_or_404("PPDK not found")
        new_admin = Admin(
            email=args["email"],
            nama=args["nama"],
            jawatan=args["jawatan"],
            ppdk_id=ppdk.id,
            password=f_bcrypt.generate_password_hash(args["no_tel"]),
        )
        phone = Phone(no_tel=args["no_tel"], admin=new_admin)

        db.session.add_all([new_admin, phone])
        db.session.commit()

        return new_admin, 201


class AdminPPDK(Resource):
    @marshal_with(adminFields)
    def get(self, id):
        ppdk = Admin.query.filter_by(id=id, role_id=2).first_or_404()
        return ppdk, 200

    def put(self, id):
        args = adminParser.parse_args()
        ppdk = Admin.query.filter_by(id=id).first_or_404()
        ppdk.nama = args["nama"]
        ppdk.jawatan = args["jawatan"]
        ppdk.ppdk_id = args["ppdk_id"]
        ppdk.no_tel = args["no_tel"]

        db.session.commit()

        return {"message": "Berjaya kemas kini"}, 200


api.add_resource(ListAdminPPDK, "/")
api.add_resource(AdminPPDK, "/<int:id>")
