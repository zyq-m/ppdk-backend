from app import app, db
from model import Admin, Jantina, Role, PPDK, Phone
from extensions import f_bcrypt


def seed_db():
    db.create_all()

    superAdmin = Role(name="super-admin")
    admin = Role(name="admin")
    pelatih = Role(name="pelatih")

    lelaki = Jantina(jantina="Lelaki")
    perempuan = Jantina(jantina="Perempuan")

    ppdk = PPDK(nama="Super PPDK", alamat="Super PPDK")
    superAcc = Admin(
        email="admin@ppdk.com",
        nama="Super",
        jawatan="Super Admin",
        ppdk=ppdk,
        password=f_bcrypt.generate_password_hash("ppdk2024"),
        role=superAdmin,
    )
    superPhone = Phone(no_tel="01119650612", admin=superAcc)

    db.session.add_all(
        [superAdmin, admin, pelatih, lelaki, perempuan, ppdk, superAcc, superPhone]
    )
    db.session.commit()


with app.app_context():
    seed_db()
