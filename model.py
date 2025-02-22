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
    no_tel = db.relationship("Phone", backref="ppdk_lookup", uselist=False)


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
    no_oku = db.Column(db.String(100), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), default=3, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    jantina = db.Column(db.String(10), nullable=False)
    agama = db.Column(db.String(100), nullable=False)
    kaum = db.Column(db.String(100), nullable=False)
    bil_adik = db.Column(db.Integer, nullable=False)
    anak_ke = db.Column(db.Integer, nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    negeri = db.Column(db.String(255), nullable=False)
    daftar_oleh = db.Column(db.Integer, db.ForeignKey("admin_ppdk.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    dtg_sendiri = db.Column(db.String(1), nullable=False)
    ya_dtg = db.Column(db.String(50), nullable=True)
    tidak_dtg = db.Column(db.String(1), nullable=True)
    is_lawat = db.Column(db.String(1), nullable=False)
    keperluan = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.Text, nullable=False)

    assessment = db.relationship("Assessment", backref="pelatih")
    penjaga = db.relationship("Penjaga", backref="pelatih")
    no_tel = db.relationship("Phone", backref="pelatih")
    keupayaan = db.relationship("TahapKeupayaan", backref="pelatih", uselist=False)
    tambahan = db.relationship("MaklumatTambahan", backref="pelatih", uselist=False)


class TahapKeupayaan(db.Model):
    __tablename__ = "keupayaan"

    id = db.Column(db.Integer, primary_key=True)
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)
    tahap_oku = db.Column(db.String(10), nullable=False)
    is_bantuan = db.Column(db.String(1), nullable=False)
    alat_bantuan = db.Column(db.String(50), nullable=True)
    penyakit = db.Column(db.String(50), nullable=True)
    sikap = db.Column(db.String(20), nullable=False)
    lain_sikap = db.Column(db.String(50), nullable=True)
    urus_diri = db.Column(db.JSON, nullable=False)
    bergerak = db.Column(db.JSON, nullable=False)


class MaklumatTambahan(db.Model):
    __tablename__ = "tambahan"

    id = db.Column(db.Integer, primary_key=True)
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)

    bersekolah = db.Column(db.String(1), nullable=False)
    nama_sek = db.Column(db.String(100), nullable=True)
    tahap_sek = db.Column(db.Integer, nullable=True)
    tempoh_sek = db.Column(db.Integer, nullable=True)
    mula_sek = db.Column(db.Date, nullable=True)
    tamat_sek = db.Column(db.Date, nullable=True)

    pemulihan = db.Column(db.String(1), nullable=False)
    nama_pem = db.Column(db.String(100), nullable=True)
    tempoh_pem = db.Column(db.Integer, nullable=True)
    mula_pem = db.Column(db.Date, nullable=True)
    tamat_pem = db.Column(db.Date, nullable=True)


class KategoriOKU(db.Model):
    __tablename__ = "oku_lookup"

    id = db.Column(db.Integer, primary_key=True)
    kategori = db.Column(db.String(255), nullable=False)
    min_umur = db.Column(db.Integer, nullable=True)
    max_umur = db.Column(db.Integer, nullable=True)
    skor = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())

    kriteria_list = db.relationship("SoalanConfig", backref="kategori_oku")
    soalan_list = db.relationship("Soalan", backref="kategori_oku")
    assessments = db.relationship("Assessment", backref="kategori_oku")


class Penjaga(db.Model):
    __tablename__ = "penjaga"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    no_kp = db.Column(db.String(12), unique=True)
    dob = db.Column(db.Date, nullable=False)
    pekerjaan = db.Column(db.String(100), nullable=False)
    pendapatan = db.Column(db.String(2), nullable=False)
    hubungan = db.Column(db.String(100), nullable=False)
    oku = db.Column(db.String(100), nullable=True)

    bantuan = db.Column(db.String(1), nullable=False)
    nama_ban = db.Column(db.String(100), nullable=True)
    kadar_ban = db.Column(db.Integer, nullable=True)
    agensi_ban = db.Column(db.String(100), nullable=True)

    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())


class SoalanConfig(db.Model):
    __tablename__ = "soalan_conf"

    id = db.Column(db.Integer, primary_key=True)
    kategori_id = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"), nullable=False)
    kriteria = db.Column(db.String(100), nullable=False)
    purata_skor = db.Column(db.JSON, nullable=False)

    soalan = db.relationship("Soalan", backref="soalan_conf")


class Soalan(db.Model):
    __tablename__ = "soalan"

    id = db.Column(db.Integer, primary_key=True)
    kategori_id = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"), nullable=False)
    kriteria_id = db.Column(db.Integer, db.ForeignKey("soalan_conf.id"), nullable=False)
    soalan = db.Column(db.Text, nullable=False)
    skor = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Assessment(db.Model):
    __tablename__ = "assessment"

    id = db.Column(db.Integer, primary_key=True)
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=False)
    jawapan = db.Column(db.JSON)
    skor = db.Column(db.JSON, nullable=False)
    skor_kriteria = db.Column(db.JSON, nullable=False)
    kategori_id = db.Column(db.Integer, db.ForeignKey("oku_lookup.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())


class Phone(db.Model):
    __tablename__ = "notel_lookup"

    id = db.Column(db.Integer, primary_key=True)
    no_tel = db.Column(db.String(13), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admin_ppdk.id"), nullable=True)
    penjaga_id = db.Column(db.Integer, db.ForeignKey("penjaga.id"), nullable=True)
    pelatih_id = db.Column(db.Integer, db.ForeignKey("pelatih.id"), nullable=True)
    ppdk_id = db.Column(db.Integer, db.ForeignKey("ppdk_lookup.id"), nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
