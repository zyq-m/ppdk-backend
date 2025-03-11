from flask import Blueprint, jsonify
import model
import json

bp = Blueprint("load", __name__, url_prefix="/load")


@bp.get('/soalan')
def load_soalan():
    soalan_list = model.Soalan.query.order_by(model.Soalan.kategori_id).all()
    data = [
        {
            "kategori": soalan.kategori_id,
            "soalan": soalan.soalan,
            "skor": soalan.skor,
        } for soalan in soalan_list]

    return jsonify(data), 200


@bp.get('/oku')
def load_oku():
    oku_list = model.KategoriOKU.query.all()
    data = [
        {
            "kategori": oku.kategori,
            "min_umur": oku.min_umur,
            "max_umur": oku.max_umur,
            "skor": oku.skor,
            "kriteria": [
                {
                    "kriteria": kriteria.kriteria,
                    "purata": kriteria.purata_skor,
                } for kriteria in oku.kriteria_list]
        } for oku in oku_list]

    return jsonify(data), 200
