from app import app, db
from model import Admin, Role, PPDK, Phone
from extensions import f_bcrypt


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
    db.session.commit()


with app.app_context():
    seed_db()
