from sqlalchemy import func, Integer, cast, case
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import Assessment, Pelatih, Admin, PPDK, db, SoalanConfig
from CONSTANT import NEGERI
import json


class Analytic(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()

        data = {
            "ppdk": PPDK.query.count(),
            "petugas": Admin.query.count(),
            "pelatih": Pelatih.query.count(),
            "penilaian": Assessment.query.count()
        }

        if user['roleId'] == 2:
            data = {
                "petugas": Admin.query.filter_by(ppdk_id=user['ppdkId']).count(),
                "pelatih": Pelatih.query.filter_by(ppdk_id=user['ppdkId']).count(),
                "penilaian": db.session.query(Assessment.id)
                .join(Pelatih)
                .join(Admin)
                .filter(Admin.ppdk_id == user['ppdkId'])
                .distinct()
                .count()
            }

        return data, 200


class Ppdk(Resource):
    @jwt_required()
    def get(self):
        counts = PPDK.query.with_entities(PPDK.negeri, func.count()).group_by(
            PPDK.negeri).order_by(PPDK.negeri.asc()).all()

        # Convert the result to a dictionary for easy lookup
        count_dict = dict(counts)

        # Create a list of dictionaries with negeri and count
        result = [
            {"negeri": negeri, "count": count_dict.get(negeri, 0)}
            for negeri in NEGERI
        ]

        return result, 200


class AnPelatih(Resource):
    @jwt_required()
    def get(self):
        # Query to get male/female counts per negeri
        counts = (
            Pelatih.query
            .with_entities(
                Pelatih.negeri,
                cast(func.sum(case((Pelatih.jantina == 1, 1), else_=0)),
                     Integer).label('lelaki'),
                cast(func.sum(case((Pelatih.jantina == 2, 1), else_=0)),
                     Integer).label('perempuan')
            )
            .group_by(Pelatih.negeri)
            .order_by(Pelatih.negeri.asc())
            .all()
        )

        # Convert the result to a dictionary for easy lookup
        count_dict = {
            negeri: {"lelaki": lelaki, "perempuan": perempuan}
            for negeri, lelaki, perempuan in counts
        }

        # Create a list of dictionaries with negeri and counts
        result = [
            {
                "negeri": negeri,
                "lelaki": count_dict.get(negeri, {}).get("lelaki", 0),
                "perempuan": count_dict.get(negeri, {}).get("perempuan", 0)
            }
            for negeri in NEGERI
        ]

        return result, 200


class AnPenilaian(Resource):
    @jwt_required()
    def get(self):
        # Get kategori id from query params
        kat_id = request.args.get('id')
        negeri = request.args.get('negeri')

        if not kat_id:
            return {'message': 'Sila pilih kategori'}, 400

        # Step 1: Initialize lookup with all kriteria and zero counts
        all_kriteria = SoalanConfig.query.filter_by(kategori_id=kat_id).all()

        lookup = {
            k.id: {"kriteria": k.kriteria, "value": 0}
            for k in all_kriteria
        }

        # Step 2: Process assessments
        assessments = db.session.query(Assessment).join(
            Assessment.pelatih).filter(Assessment.kategori_id == kat_id)

        if negeri:
            assessments = assessments.filter(Pelatih.negeri == negeri)

        assessments = assessments.all()

        for assess in assessments:
            skor = json.loads(assess.skor_kriteria)
            max_value = max(skor.values())

            for k, v in skor.items():
                if v == max_value:
                    k_id = int(k)  # Convert key to int if needed
                    if k_id in lookup:
                        lookup[k_id]['value'] += 1

        # Step 3: Prepare result as list of objects
        result = list(lookup.values())

        return result, 200
