from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_jwt_extended import jwt_required

from model import db, Admin, PPDK, Phone
from extensions import f_bcrypt

bp = Blueprint("admin-ppdk", __name__, url_prefix="/admin-ppdk")
api = Api(bp)

adminParser = reqparse.RequestParser()
adminParser.add_argument("email", type=str, required=True)
adminParser.add_argument("nama", type=str, required=True)
adminParser.add_argument("notel", type=str, required=True)
adminParser.add_argument("jawatan", type=str, required=True)
adminParser.add_argument("ppdk", type=str, required=True)
adminParser.add_argument("active", type=bool, required=False)

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
    @jwt_required()
    @marshal_with(adminFields)
    def get(self):
        ppdk = Admin.query.filter(Admin.active).all()
        return ppdk, 200

    @jwt_required()
    def post(self):
        args = adminParser.parse_args()
        ppdk = PPDK.query.filter_by(
            id=args["ppdk"]).first_or_404("PPDK not found")
        new_admin = Admin(
            email=args["email"],
            nama=args["nama"],
            jawatan=args["jawatan"],
            password=f_bcrypt.generate_password_hash("ppdk2024"),
            ppdk=ppdk,
        )
        phone = Phone(no_tel=args["notel"], admin=new_admin)

        db.session.add_all([new_admin, phone])
        db.session.commit()

        return {"message": "Admin berjaya didaftarkan"}, 201


class AdminPPDK(Resource):
    @jwt_required()
    @marshal_with(adminFields)
    def get(self, id):
        ppdk = Admin.query.filter_by(id=id, role_id=2).first_or_404()
        return ppdk, 200

    @jwt_required()
    def put(self, id):
        args = adminParser.parse_args()
        admin = Admin.query.filter_by(id=id).first_or_404("Admin tidak wujud")

        admin.email = args.get("email") or admin.email
        admin.nama = args.get("nama") or admin.nama
        admin.jawatan = args.get("jawatan") or admin.jawatan
        admin.active = args.get("active") or admin.active

        if args.get("notel"):
            notel = Phone.query.filter_by(admin=admin).first()
            if notel:
                notel.no_tel = args.get("notel")
            else:
                notel = Phone(admin=admin, no_tel=args.get("notel"))
                db.session.add(notel)

        db.session.commit()

        if args.get("active"):
            return {"message": "Admin berjaya dipadam"}, 200

        return {"message": "Berjaya kemas kini"}, 200


api.add_resource(ListAdminPPDK, "")
api.add_resource(AdminPPDK, "/<int:id>")
