import ast
from flask import Blueprint, json, request
from flask_restful import Api, Resource, fields, reqparse, abort, marshal_with
from flask_jwt_extended import jwt_required

from model import db, Assessment

bp = Blueprint("assessment", __name__, url_prefix="/assessment")
api = Api(bp)

assessmentParser = reqparse.RequestParser()
assessmentParser.add_argument("pelatih_id", type=str, required=True)
assessmentParser.add_argument("jawapan", type=str, required=True)

assessmentFields = {
    "id": fields.String,
    "jawapan": fields.String,
    "kategori_oku": fields.Nested(
        {
            "id": fields.String,
            "kategori": fields.String,
        }
    ),
    "created_at": fields.String,
}


class Assess(Resource):
    @marshal_with(assessmentFields)
    def get(self, id):
        assessment = Assessment.query.filter_by(
            kategori_id=id, pelatih_id=request.args.get("pelatih_id")
        ).first()

        return assessment, 200

    def post(self, id):
        args = assessmentParser.parse_args()
        assessment = Assessment.query.filter_by(
            pelatih_id=args["pelatih_id"], kategori_id=id
        ).first()

        if assessment:
            assessment.jawapan = args["jawapan"]
        else:
            new_assessment = Assessment(
                pelatih_id=args["pelatih_id"],
                jawapan=args["jawapan"],
                kategori_id=id,
            )
            db.session.add(new_assessment)

        db.session.commit()

        return {"message": "Berjaya disimpan"}, 201

    def put(self):
        pass

    def delete(self):
        pass


api.add_resource(Assess, "/<int:id>")
