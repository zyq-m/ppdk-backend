from extensions import db
from sqlalchemy.sql import func


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    admins = db.relationship("Admin", backref="role")
    pelatih = db.relationship("Pelatih", backref="role")


class PPDK(db.Model):
    __tablename__ = "ppdk_lookup"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(80), nullable=False)
    negeri = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    admins = db.relationship("Admin", backref="ppdk")
    no_tel = db.relationship("Phone", backref="ppdk_lookup")


class Admin(db.Model):
    __tablename__ = "admin_ppdk"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nama = db.Column(db.Text, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), default=2, nullable=False)
    jawatan = db.Column(db.String(80))
    password = db.Column(db.Text, nullable=False)
    ppdk_id = db.Column(db.Integer, db.ForeignKey("ppdk_lookup.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    no_tel = db.relationship("Phone", backref="admin")
    pelatih_list = db.relationship("Pelatih", backref="admin_ppdk")


class Pelatih(db.Model):
    __tablename__ = "pelatih"

    id = db.Column(db.Integer, primary_key=True)
    no_kp = db.Column(db.String(12), unique=True)
    nama = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), default=3, nullable=False)
    kaum = db.Column(db.String(255), nullable=False)
    jantina_id = db.Column(
        db.Integer, db.ForeignKey("jantina_lookup.id"), nullable=False
    )
    alamat = db.Column(db.Text, nullable=False)
    negeri = db.Column(db.String(255), nullable=False)
    daftar_oleh = db.Column(db.Integer, db.ForeignKey("admin_ppdk.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    assessment = db.relationship("Assessment", backref="pelatih")
    penjaga = db.relationship("Penjaga", backref="pelatih")


class KategoriOKU(db.Model):
    __tablename__ = "oku_lookup"

    id = db.Column(db.Integer, primary_key=True)
    kategori = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    soalan_list = db.relationship("Soalan", backref="kategori_oku")
    assessments = db.relationship("Assessment", backref="kategori_oku")


class Penjaga(db.Model):
    __tablename__ = "penjaga"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    hubungan = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)

    no_tel = db.relationship("Phone", backref="penjaga")
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=func.now())


class Soalan(db.Model):
    __tablename__ = "soalan"

    id = db.Column(db.Integer, primary_key=True)
    kategori_id = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"), nullable=False)
    soalan = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)
    jawapan = db.Column(db.JSON)
    skor = db.Column(db.Double)
    kategori_id = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    result = db.relationship("AssessmentResult", backref="assessment", uselist=False)


class AssessmentResult(db.Model):
    __tablename__ = "assess_res"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessment.id"), unique=True, nullable=False
    )
    result = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"))
    created_at = db.Column(db.DateTime, server_default=func.now())


# look up model
class Phone(db.Model):
    __tablename__ = "notel_lookup"

    id = db.Column(db.Integer, primary_key=True)
    no_tel = db.Column(db.String(13), unique=True, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin_ppdk.id"), nullable=True)
    penjaga_id = db.Column(db.Integer, db.ForeignKey("penjaga.id"), nullable=True)
    ppdk_id = db.Column(db.Integer, db.ForeignKey("ppdk_lookup.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Jantina(db.Model):
    __tablename__ = "jantina_lookup"

    id = db.Column(db.Integer, primary_key=True)
    jantina = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    pelatih_list = db.relationship("Pelatih", backref="jantina")
