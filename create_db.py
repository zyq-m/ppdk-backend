from app import app, db
from model import (
    Admin,
    Role,
    PPDK,
    Phone,
    KategoriOKU, Soalan, SoalanConfig
)
from extensions import f_bcrypt
import json


def seed_db():
    db.create_all()

    superAdmin = Role(name="super-admin")
    adminRole = Role(name="admin")
    pelatihRole = Role(name="pelatih")

    ppdk = PPDK(nama="Super PPDK", alamat="Super PPDK", negeri="Terengganu")
    superAcc = Admin(
        email="admin@ppdk.com",
        nama="Super",
        jawatan="Super Admin",
        ppdk=ppdk,
        password=f_bcrypt.generate_password_hash("ppdk2024"),
        role=superAdmin,
    )
    admin = Admin(
        email="ahmad@ppdk.com",
        nama="Ahmad",
        jawatan="Penyelia",
        ppdk=ppdk,
        password=f_bcrypt.generate_password_hash("ppdk2024"),
    )
    superPhone = Phone(no_tel="01119650612", admin=superAcc)
    adminPhone = Phone(no_tel="01119650613", admin=admin)
    seed_soalan()

    db.session.add_all(
        [
            superAdmin,
            adminRole,
            pelatihRole,
            ppdk,
            superAcc,
            admin,
            superPhone,
            adminPhone,
        ]
    )


def seed_soalan():
    # seed kategori
    # seed soalan & kriteria
    with open('seed/soalan.json', 'r') as soalan:
        soalan_json = json.load(soalan)
    for kategori in soalan_json:
        kat = KategoriOKU(
            kategori=kategori.get("kategori"),
            min_umur=kategori.get("min_umur"),
            max_umur=kategori.get("max_umur"),
            pemarkahan=1,
            skor=kategori.get("skor"),
        )
        kriteria_list = [
            SoalanConfig(
                kriteria=kriteria.get('kriteria'),
                purata_skor=kriteria.get('purata'),
                kategori_oku=kat,
                soalan=[
                    Soalan(
                        soalan=soalan.get('soalan'),
                        skor=soalan.get('skor'),
                        kategori_oku=kat
                    ) for soalan in kriteria.get('soalan')]
            ) for kriteria in kategori.get('kriteria')]
        db.session.add_all(kriteria_list)

with app.app_context():
    seed_soalan()
    db.session.commit()
