from flask import Blueprint, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from model import PPDK, Admin, Phone
from extensions import f_bcrypt, db

bp = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(bp)

adminFields = {
    "email": fields.String,
    "nama": fields.String,
    "ppdk": fields.String,
}

login_parser = reqparse.RequestParser()
login_parser.add_argument(
    "email", type=str, required=True, help="Email cannot be blank"
)
login_parser.add_argument(
    "password", type=str, required=True, help="Password cannot be blank"
)

signup = reqparse.RequestParser()
signup.add_argument("email", type=str, required=True)
signup.add_argument("nama", type=str, required=True)
signup.add_argument("no_tel", type=str, required=True)
signup.add_argument("jawatan", type=str, required=True)
signup.add_argument("ppdk_id", type=str, required=True)

password = reqparse.RequestParser()
password.add_argument("email", type=str, required=True)
password.add_argument("new_pass", type=str, required=True)


class Login(Resource):
    def post(self):
        args = login_parser.parse_args()
        admin = Admin.query.filter_by(email=args["email"]).first_or_404(
            "User not found"
        )

        if not f_bcrypt.check_password_hash(admin.password, args["password"]):
            abort(400, message="Invalid password")

        admin_payload = {
            "email": admin.email,
            "roleId": admin.role_id,
            "ppdkId": admin.ppdk_id,
        }
        token = {
            "accessToken": create_access_token(str(admin_payload)),
            "refreshToken": create_refresh_token(str(admin_payload)),
        }

        return token, 200


class Signup(Resource):
    @marshal_with(adminFields)
    def post(self):
        args = signup.parse_args()
        ppdk = PPDK.query.filter_by(id=args["ppdk_id"]).first_or_404("PPDK not found")
        new_admin = Admin(
            email=args["email"],
            nama=args["nama"],
            jawatan=args["jawatan"],
            ppdk_id=ppdk.id,
            password=f_bcrypt.generate_password_hash("ppdk2024"),
        )
        phone = Phone(no_tel=args["no_tel"], admin=new_admin)

        db.session.add_all([new_admin, phone])
        db.session.commit()

        return new_admin, 201


class Password(Resource):
    def put(self):
        args = password.parse_args()
        admin = Admin.query.filter_by(email=args["email"]).first_or_404(
            "Admin not found"
        )
        admin.password = f_bcrypt.generate_password_hash(args["new_pass"])

        db.session.commit()

        return {"message": "Berjaya kemaskini katalaluan"}, 200


class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        token = {"accessToken": create_access_token(identity=identity)}

        return token, 200


api.add_resource(Login, "/login")
api.add_resource(Signup, "/signup")
api.add_resource(RefreshToken, "/refresh")
api.add_resource(Password, "/password")
