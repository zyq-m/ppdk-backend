from flask import Blueprint
from flask_restful import Api

from controllers.analytic import Analytic, Ppdk, AnPelatih, AnPenilaian

bp = Blueprint("analytic", __name__, url_prefix="/analytic")
api = Api(bp)

api.add_resource(Analytic, "")
api.add_resource(Ppdk, "/ppdk")
api.add_resource(AnPelatih, "/pelatih")
api.add_resource(AnPenilaian, "/penilaian")
