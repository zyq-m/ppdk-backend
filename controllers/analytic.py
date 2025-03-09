from sqlalchemy import func, Integer, cast, case
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from model import Assessment, Pelatih, Admin, PPDK, KategoriOKU
from CONSTANT import NEGERI
import ast
from utils.score import ScoreCalculator


class Analytic(Resource):
    @jwt_required()
    def get(self):
        data = {
            "ppdk": PPDK.query.count(),
            "petugas": Admin.query.count(),
            "pelatih": Pelatih.query.count(),
            "penilaian": Assessment.query.count()
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
        # Initialize lookup with all categories pre-defined
        lookup = {}
        special_kategori = {1, 2}  # Using set for faster lookups

        # Pre-populate lookup for all categories
        all_kategori = KategoriOKU.query.all()
        for kat in all_kategori:
            # Determine category name based on availability of min_umur and max_umur
            if kat.min_umur and kat.max_umur:
                name = f"{kat.kategori} ({kat.min_umur}-{kat.max_umur} tahun)"
            else:
                name = kat.kategori

            lookup[kat.id] = {
                'rendah': 0,
                'sederhana': 0,
                'tinggi': 0,
                'keseluruhan': 0,
                'name': name
            }

        # Process assessments
        assessments = Assessment.query.all()
        for assessment in assessments:
            jawapan = ast.literal_eval(assessment.jawapan)
            kategori_id = assessment.kategori_id

            if kategori_id in special_kategori:
                # Process special categories
                score = ScoreCalculator(jawapan)
                indicator = score.classify_score()

                # Update counts for special categories
                if indicator == "Rendah":
                    lookup[kategori_id]['rendah'] += 1
                elif indicator == "Sederhana":
                    lookup[kategori_id]['sederhana'] += 1
                elif indicator == "Tinggi":
                    lookup[kategori_id]['tinggi'] += 1

            # Process non-special categories
            if kategori_id not in special_kategori and assessment.kategori_oku:
                kat_id = assessment.kategori_oku.id
                lookup[kat_id]['keseluruhan'] += 1

        # Build result based on all categories
        result = [
            {
                "kategori": lookup.get(kat.id, {}).get('name', kat.kategori),
                "rendah": lookup.get(kat.id, {}).get('rendah', 0),
                "sederhana": lookup.get(kat.id, {}).get('sederhana', 0),
                "tinggi": lookup.get(kat.id, {}).get('tinggi', 0),
                "keseluruhan": lookup.get(kat.id, {}).get('keseluruhan', 0),
            }
            for kat in all_kategori
        ]

        return result, 200
