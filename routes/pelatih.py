import ast
import os
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.score import ScoreCalculator
from utils.umur import UmurCalculator
from cerberus import Validator
from utils.formSchema import pelatihSchema
from werkzeug.utils import secure_filename
import json

from model import db, Admin, Phone, Pelatih, Penjaga, TahapKeupayaan, MaklumatTambahan
from CONSTANT import ALLOWED_EXTENSIONS
from routes.assessment import assessmentFields

bp = Blueprint("pelatih", __name__, url_prefix="/pelatih")
api = Api(bp)

pelatihParser = reqparse.RequestParser()

pelatihFields = {
    "id": fields.String,
    "nama": fields.String,
    "no_kp": fields.String,
    "no_pendaftaran": fields.String(attribute="no_oku"),
    "dob": fields.String,
    "bangsa": fields.String(attribute="kaum"),
    "umur": fields.Integer,
    "jantina": fields.String,
    "negeri": fields.String,
}

penjagaField = {
    "nama": fields.String,
    "noKp": fields.String(attribute="no_kp"),
    "dob": fields.String,
    "pekerjaan": fields.String,
    "pendapatan": fields.String,
    "hubungan": fields.String,
    "ketidakUpayaan": fields.String(attribute="oku"),
    "isPenerima": fields.String(attribute="bantuan"),
    "bantuan": fields.String(attribute="nama_ban"),
    "kadar": fields.String(attribute="kadar_ban"),
    "agensi": fields.String(attribute="agensi_ban"),
}

keupayaanField = {
    "tahapOKU": fields.String(attribute="tahap_oku"),
    "isBantuan": fields.String(attribute="is_bantuan"),
    "alatBantuan": fields.String(attribute="alat_bantuan"),
    "penyakit": fields.String,
    "sikap": fields.String,
    "lainSikap": fields.String(attribute="lain_sikap"),
    "urusDiri": fields.List(fields.String, attribute="urus_diri"),
    "bergerak": fields.List(fields.String),
}

tambahanField = {
    "isSekolah": fields.String(attribute="bersekolah"),
    "namaSek": fields.String(attribute="nama_sek"),
    "tahapSek": fields.String(attribute="tahap_sek"),
    "tempohSek": fields.String(attribute="tempoh_sek"),
    "mulaSek": fields.String(attribute="mula_sek"),
    "tamatSek": fields.String(attribute="tamat_sek"),
    "isInsitusi": fields.String(attribute="pemulihan"),
    "namaIns": fields.String(attribute="nama_pem"),
    "mulaIns": fields.String(attribute="mula_pem"),
    "tamatIns": fields.String(attribute="tamat_pem"),
}
penilaianField = {
    "id": fields.String,
    "skor": fields.Integer,
    "indicator": fields.String,
    "kategori_oku": fields.Nested(
        {
            "id": fields.String,
            "kategori": fields.String,
        }
    ),
    "created_at": fields.String,
}

extendFields = {
    "bilAdik": fields.String(attribute="bil_adik"),
    "bilKeluarga": fields.String(attribute="anak_ke"),
    "alamat": fields.String,
    "agama": fields.String,
    "avatar": fields.String,
    "dtgSendiri": fields.String(attribute="dtg_sendiri"),
    "yaDtg": fields.String(attribute="ya_dtg"),
    "tidakDtg": fields.String(attribute="tidak_dtg"),
    "sudahLawat": fields.String(attribute="is_lawat"),
    "keperluan": fields.String,
    "no_tel": fields.List(
        fields.Nested({"no": fields.String(
            attribute="no_tel"), "type": fields.String})
    ),
    "penjaga": fields.List(fields.Nested(penjagaField)),
    "keupayaan": fields.Nested(keupayaanField),
    "tambahan": fields.Nested(tambahanField),
    "assessment": fields.Nested(penilaianField),
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ListPelatih(Resource):
    @marshal_with({**pelatihFields, "assessment": fields.Nested(assessmentFields)})
    @jwt_required()
    def get(self):
        payload = get_jwt_identity()
        admin_ppdk = Admin.query.filter_by(
            email=payload.get("email")).first_or_404()
        pelatih = Pelatih.query.filter_by(admin_ppdk=admin_ppdk).all()

        if payload["roleId"] == 1:
            pelatih = Pelatih.query.all()

        for p in pelatih:
            umur = UmurCalculator(p.no_kp)
            p.umur = umur.get_age()
            p.jantina = "Lelaki" if p.jantina == "1" else "Perempuan"

        return pelatih, 200

    @jwt_required()
    def post(self):
        payload = get_jwt_identity()
        avatar = request.files.get("img")

        if avatar is None:
            return {"message": "Sila upload gambar"}, 400

        if not allowed_file(avatar.filename):
            return {"message": "Format gambar hendaklah dalam jpg, jpeg atau png"}, 400

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        filename = secure_filename(avatar.filename)
        avatar.save(os.path.join(upload_folder, filename))

        fd = request.form.get("json")
        args = json.loads(fd)

        # v = Validator(pelatihSchema)
        # if not v.validate(arg):
        #     return "error", 400

        admin_ppdk = Admin.query.filter_by(
            email=payload.get("email")).first_or_404()

        umur = UmurCalculator(args.get('no_kp'))

        new_pelatih = Pelatih(
            nama=args.get("nama"),
            jantina=args.get("jantina"),
            no_kp=args.get("no_kp"),
            no_oku=args.get("no_pendaftaran"),
            dob=umur.get_dob(),
            agama=args.get("agama"),
            kaum=args.get("bangsa"),
            bil_adik=args.get("bilAdik"),
            anak_ke=args.get("bilKeluarga"),
            alamat=args.get("alamat"),
            negeri=args.get("negeri"),
            avatar=filename,
            dtg_sendiri=args.get("dtgSendiri"),
            ya_dtg=args.get("yaDtg"),
            tidak_dtg=args.get("tidakDtg"),
            is_lawat=args.get("sudahLawat"),
            keperluan=args.get("keperluan"),
            daftar_oleh=admin_ppdk.id,
            ppdk_id=admin_ppdk.ppdk_id
        )

        k = args.get("keupayaan")
        new_keu = TahapKeupayaan(
            pelatih=new_pelatih,
            tahap_oku=k.get("tahapOKU"),
            is_bantuan=k.get("isBantuan"),
            alat_bantuan=k.get("alatBantuan"),
            penyakit=k.get("penyakit"),
            sikap=k.get("sikap"),
            lain_sikap=k.get("lainSikap"),
            urus_diri=k.get("urusDiri"),
            bergerak=k.get("bergerak"),
        )

        t = args.get("tambahan")
        new_tam = MaklumatTambahan(
            pelatih=new_pelatih,
            bersekolah=t.get("isSekolah"),
            nama_sek=t.get("namaSek"),
            tahap_sek=t.get("tahapSek"),
            tempoh_sek=t.get("tempohSek"),
            mula_sek=t.get("mulaSek"),
            tamat_sek=t.get("tamatSek"),
            pemulihan=t.get("isInsitusi"),
            nama_pem=t.get("namaIns"),
            tempoh_pem=t.get("tempohIns"),
            mula_pem=t.get("mulaIns"),
            tamat_pem=t.get("tamatIns"),
        )

        for pen in args.get("penjaga"):
            umur_pen = UmurCalculator(pen.get('noKp'))
            penjaga = Penjaga(
                pelatih=new_pelatih,
                nama=pen.get("nama"),
                no_kp=pen.get("noKp"),
                dob=umur_pen.get_dob(),
                pekerjaan=pen.get("pekerjaan"),
                pendapatan=pen.get("pendapatan"),
                hubungan=pen.get("hubungan"),
                oku=pen.get("ketidakUpayaan"),
                bantuan=pen.get("isPenerima"),
                nama_ban=pen.get("bantuan"),
                kadar_ban=pen.get("kadar"),
                agensi_ban=pen.get("agensi"),
            )
            db.session.add(penjaga)

        no_tel = [
            Phone(
                pelatih=new_pelatih,
                no_tel=noTel.get("no"),
                type=noTel.get("type"),
            )
            for noTel in args.get("no_tel")
        ]

        db.session.add_all(
            [new_pelatih, *no_tel, new_keu, new_tam])
        db.session.commit()

        return {"message": "Berjaya didaftarkan"}, 201


class PelatihInfo(Resource):
    @marshal_with({**pelatihFields, **extendFields})
    @jwt_required()
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


api.add_resource(ListPelatih, "")
api.add_resource(PelatihInfo, "/<int:id>")
