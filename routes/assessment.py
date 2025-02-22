import ast
from flask import Blueprint, json, request
from flask_restful import Api, Resource, fields, reqparse, abort, marshal_with
from flask_jwt_extended import jwt_required
from utils.score import ScoreCalculator
from utils.umur import UmurCalculator

from routes.setup import extendedSoalan

from model import db, Assessment

bp = Blueprint("assessment", __name__, url_prefix="/assessment")
api = Api(bp)

assessmentParser = reqparse.RequestParser()
assessmentParser.add_argument("pelatih_id", type=str, required=True)
assessmentParser.add_argument("jawapan", type=str, required=True)

assessmentFields = {
    "id": fields.String,
    "jawapan": fields.String,
    "skor": fields.Integer,
    "indicator": fields.String,
    "kategori_oku": fields.Nested(extendedSoalan),
    "created_at": fields.String,
}


class Assess(Resource):
    @jwt_required()
    @marshal_with(assessmentFields)
    def get(self, id):
        assessment = Assessment.query.filter_by(
            kategori_id=id, pelatih_id=request.args.get("pelatih_id")
        ).first_or_404("Pelatih tidak ditemui")

        # for p in assessment:
        jawapan = ast.literal_eval(assessment.jawapan)
        score = ScoreCalculator(jawapan)
        umur = UmurCalculator(assessment.pelatih.dob)

        assessment.pelatih.umur = umur.get_age()
        assessment.indicator = score.classify_score()
        assessment.lagend = score.range_score()

        return assessment, 200

    @jwt_required()
    def post(self, id):
        args = assessmentParser.parse_args()
        assessment = Assessment.query.filter_by(
            pelatih_id=args["pelatih_id"], kategori_id=id
        ).first()

        jawapan = json.loads(args["jawapan"])
        score = ScoreCalculator(jawapan)

        if assessment:
            assessment.jawapan = args["jawapan"]
            assessment.skor = score.calc_score()
        else:
            new_assessment = Assessment(
                pelatih_id=args["pelatih_id"],
                jawapan=args["jawapan"],
                kategori_id=id,
                skor=score.calc_score(),
            )
            db.session.add(new_assessment)

        db.session.commit()

        return {"message": "Berjaya disimpan"}, 201

    @jwt_required()
    def put(self):
        pass

    @jwt_required()
    def delete(self):
        pass


class ListPelatih(Resource):
    @jwt_required()
    @marshal_with(assessmentFields)
    def get(self):
        pelatih = Assessment.query.all()

        for p in pelatih:
            jawapan = ast.literal_eval(p.jawapan)
            score = ScoreCalculator(jawapan)
            umur = UmurCalculator(p.pelatih.dob)

            p.pelatih.umur = umur.get_age()
            p.indicator = score.classify_score()

        return pelatih, 200


api.add_resource(ListPelatih, "")
api.add_resource(Assess, "/<int:id>")
