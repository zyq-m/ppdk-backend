import os
from flask import Blueprint, request, current_app, jsonify
from sqlalchemy.exc import IntegrityError
from flask_restful import Api, Resource, fields, marshal_with, abort
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.score import ScoreCalculator
from utils.umur import UmurCalculator
from cerberus import Validator
from utils.formSchema import pelatihSchema
from werkzeug.utils import secure_filename
import json

from model import db, Admin, Phone, Pelatih, Penjaga, TahapKeupayaan, MaklumatTambahan
from CONSTANT import ALLOWED_EXTENSIONS, BARTHEL_SCORING_MAP, SDQ_SCORING_MAP
from routes.assessment import assessmentFields

bp = Blueprint("pelatih", __name__, url_prefix="/pelatih")
api = Api(bp)

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
    "is_aktif": fields.Boolean
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
    "kadOku": fields.String(attribute="kad_oku"),
    "dtgSendiri": fields.String(attribute="dtg_sendiri"),
    "yaDtg": fields.String(attribute="ya_dtg"),
    "tidakDtg": fields.String(attribute="tidak_dtg"),
    "sudahLawat": fields.String(attribute="is_lawat"),
    "keperluan": fields.String,
    "no_tel": fields.List(
        fields.Nested({"id": fields.String, "no": fields.String(
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
        avatar = request.files.get('avatar')
        okuImg = request.files.get('okuImg')  # kad oku
        upload_folder = current_app.config["UPLOAD_FOLDER"]

        if avatar is None:
            return {"message": "Sila upload gambar"}, 400
        if okuImg is None:
            return {"message": "Sila upload gambar kad OKU"}, 400

        if (avatar and not allowed_file(avatar.filename)) or (okuImg and not allowed_file(okuImg.filename)):
            return {"message": "Format gambar hendaklah dalam jpg, jpeg atau png"}, 400

        # secure filename
        secure_avatar = secure_filename(avatar.filename)
        secure_okuImg = secure_filename(okuImg.filename)

        if avatar and allowed_file(avatar.filename):
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            avatar.save(os.path.join(upload_folder, secure_avatar))

        if okuImg and allowed_file(okuImg.filename):
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            okuImg.save(os.path.join(upload_folder, secure_okuImg))

        fd = request.form.get("json")
        args = json.loads(fd)

        # v = Validator(pelatihSchema)
        # if not v.validate(arg):
        #     return "error", 400

        admin_ppdk = Admin.query.filter_by(
            email=payload.get("email")).first_or_404()

        # Check no ic & no oku
        ic_exist = Pelatih.query.filter_by(no_kp=args.get('no_kp')).first()
        if ic_exist:
            return {"message": "No KP pelatih telah wujud di dalam sistem."}, 400
        oku_no_exist = Pelatih.query.filter_by(
            no_oku=args.get('no_pendaftaran')).first()
        if oku_no_exist:
            return {"message": "No Pendafataran OKU telah wujud di dalam sistem."}, 400

        try:
            umur = UmurCalculator(args.get('no_kp'))
            dob_pelatih = umur.get_dob()
        except:
            return {"message": "No KP pelatih tidak betul"}, 400

        new_pelatih = Pelatih(
            nama=args.get("nama"),
            jantina=args.get("jantina"),
            no_kp=args.get("no_kp"),
            no_oku=args.get("no_pendaftaran"),
            dob=dob_pelatih,
            agama=args.get("agama"),
            kaum=args.get("bangsa"),
            bil_adik=args.get("bilAdik"),
            anak_ke=args.get("bilKeluarga"),
            alamat=args.get("alamat"),
            negeri=args.get("negeri"),
            avatar=secure_avatar,
            kad_oku=secure_okuImg,
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
            tahap_sek=int(t.get("tahapSek")) if t.get("tahapSek") else None,
            tempoh_sek=int(t.get("tempohSek")) if t.get("tempohSek") else None,
            mula_sek=t.get("mulaSek") if t.get('mulaSek') else None,
            tamat_sek=t.get("tamatSek") if t.get('tamatSek') else None,
            pemulihan=t.get("isInsitusi"),
            nama_pem=t.get("namaIns"),
            tempoh_pem=t.get("tempohIns") if t.get("tempohIns") else None,
            mula_pem=t.get("mulaIns") if t.get("mulaIns") else None,
            tamat_pem=t.get("tamatIns") if t.get("tamatIns") else None,
        )

        for pen in args.get("penjaga"):
            try:
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
                    kadar_ban=pen.get("kadar") if pen.get("kadar") else None,
                    agensi_ban=pen.get("agensi"),
                )
                db.session.add(penjaga)
            except:
                return {"message": "No KP penjaga tidak betul."}, 400

        for noTel in args.get("no_tel"):
            exist_notel = Phone.query.filter_by(no_tel=noTel.get("no")).first()
            if exist_notel:
                return {'message': f'No telefon: {noTel.get("no")} telah wujud di dalam'}, 400

            no_tel = Phone(
                pelatih=new_pelatih,
                no_tel=noTel.get("no"),
                type=noTel.get("type"),
            )
            db.session.add(no_tel)

        try:
            db.session.add_all(
                [new_pelatih, new_keu, new_tam])
            db.session.commit()

            return {"message": "Berjaya didaftarkan"}, 201
        except Exception as e:
            db.session.rollback()
            print(e)
            return {"message": "Error"}, 500


class PelatihInfo(Resource):
    @marshal_with({**pelatihFields, **extendFields})
    @jwt_required()
    def get(self, id):
        pelatih = Pelatih.query.filter_by(id=id).first_or_404()

        for p in pelatih.assessment:
            # process indicator
            if p.kategori_id in {1, 2}:
                p.indicator = SDQ_SCORING_MAP[p.label]
            else:
                p.indicator = BARTHEL_SCORING_MAP[p.label]

        umur = UmurCalculator(pelatih.no_kp)
        pelatih.umur = umur.get_age()
        return pelatih, 200

    @jwt_required()
    def put(self, id):
        pelatih = Pelatih.query.filter_by(id=id).first_or_404()

        # Update status pelatih aktif/tak aktif
        if 'json' not in request.form:
            pelatih.is_aktif = not pelatih.is_aktif

        if request.form and request.files:
            fd = request.form.get("json")
            args = json.loads(fd)
            # update avatar & oku card
            avatar = request.files.get('avatar')
            okuImg = request.files.get('okuImg')  # kad oku
            upload_folder = current_app.config["UPLOAD_FOLDER"]

            if (avatar and not allowed_file(avatar.filename)) or (okuImg and not allowed_file(okuImg.filename)):
                return {"message": "Format gambar hendaklah dalam jpg, jpeg atau png"}, 400

            # secure filename
            secure_avatar = secure_filename(
                avatar.filename) if avatar else None
            secure_okuImg = secure_filename(
                okuImg.filename) if okuImg else None

            if avatar and allowed_file(avatar.filename):
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                avatar.save(os.path.join(upload_folder, secure_avatar))

            if okuImg and allowed_file(okuImg.filename):
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                okuImg.save(os.path.join(upload_folder, secure_okuImg))

            try:
                umur = UmurCalculator(args.get('no_kp'))
                dob_pelatih = umur.get_dob()
            except:
                return {"message": "No KP pelatih tidak betul"}, 400

            # update peribadi info
            pelatih.nama = args.get("nama")
            pelatih.jantina = args.get("jantina")
            pelatih.no_kp = args.get("no_kp")
            pelatih.no_oku = args.get("no_pendaftaran")
            pelatih.dob = dob_pelatih
            pelatih.agama = args.get("agama")
            pelatih.kaum = args.get("bangsa")
            pelatih.bil_adik = args.get("bilAdik")
            pelatih.anak_ke = args.get("bilKeluarga")
            pelatih.alamat = args.get("alamat")
            pelatih.negeri = args.get("negeri")
            pelatih.dtg_sendiri = args.get("dtgSendiri")
            pelatih.ya_dtg = args.get("yaDtg")
            pelatih.tidak_dtg = args.get("tidakDtg")
            pelatih.is_lawat = args.get("sudahLawat")
            pelatih.keperluan = args.get("keperluan")
            pelatih.avatar = secure_avatar if avatar else pelatih.avatar
            pelatih.kad_oku = secure_okuImg if okuImg else pelatih.kad_oku

            # update keupayaan info
            k = args.get("keupayaan")
            pelatih.keupayaan.tahap_oku = k.get("tahapOKU")
            pelatih.keupayaan.is_bantuan = k.get("isBantuan")
            pelatih.keupayaan.alat_bantuan = k.get("alatBantuan")
            pelatih.keupayaan.penyakit = k.get("penyakit")
            pelatih.keupayaan.sikap = k.get("sikap")
            pelatih.keupayaan.lain_sikap = k.get("lainSikap")
            pelatih.keupayaan.urus_diri = k.get("urusDiri")
            pelatih.keupayaan.bergerak = k.get("bergerak")

            # tambahan info
            t = args.get("tambahan")
            pelatih.tambahan.bersekolah = t.get("isSekolah")
            pelatih.tambahan.nama_sek = t.get("namaSek")
            pelatih.tambahan.tahap_sek = t.get("tahapSek")
            pelatih.tambahan.tempoh_sek = t.get("tempohSek")
            pelatih.tambahan.mula_sek = t.get("mulaSek")
            pelatih.tambahan.tamat_sek = t.get("tamatSek")
            pelatih.tambahan.pemulihan = t.get("isInsitusi")
            pelatih.tambahan.nama_pem = t.get("namaIns")
            pelatih.tambahan.tempoh_pem = t.get("tempohIns")
            pelatih.tambahan.mula_pem = t.get("mulaIns")
            pelatih.tambahan.tamat_pem = t.get("tamatIns")

            for penjaga in pelatih.penjaga:
                for pen in args.get('penjaga'):
                    umur_pen = UmurCalculator(pen.get('noKp'))
                    try:
                        penjaga.dob = umur_pen.get_dob()
                    except:
                        return {"message": "No KP penjaga tidak betul."}, 400

                    penjaga.nama = pen.get("nama")
                    penjaga.no_kp = pen.get("noKp")
                    penjaga.pekerjaan = pen.get("pekerjaan")
                    penjaga.pendapatan = pen.get("pendapatan")
                    penjaga.hubungan = pen.get("hubungan")
                    penjaga.oku = pen.get("ketidakUpayaan")
                    penjaga.bantuan = pen.get("isPenerima")
                    penjaga.nama_ban = pen.get("bantuan")
                    penjaga.kadar_ban = pen.get("kadar")
                    penjaga.agensi_ban = pen.get("agensi")

            # Create a map from id to phone data from the payload
            new_phones_map = {int(phone["id"]): phone for phone in args.get(
                "no_tel") if phone.get("id")}

            # update existing phone number
            for phone in pelatih.no_tel:
                if phone.id in new_phones_map:
                    updated_data = new_phones_map[phone.id]
                    phone.no_tel = updated_data.get("no", phone.no_tel)
                    phone.type = updated_data.get("type", phone.type)

        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return {"message": "Server error"}, 500

        return {"message": "Maklumat pelatih berjaya dikemaskini"}, 200

    @jwt_required()
    def delete(self, id):
        # find pelatih
        Pelatih.query.filter_by(id=id).first_or_404("Pelatih tidak dijumpai")

        try:
            # Delete pelatih
            Pelatih.query.filter_by(id=id).delete()
            db.session.commit()

            return {"message": "Pelatih berjaya dipadam"}

        except Exception as e:
            db.session.rollback()
            print(e)
            return {"message": "Gagal memadam pelatih"}, 500


api.add_resource(ListPelatih, "")
api.add_resource(PelatihInfo, "/<int:id>")
