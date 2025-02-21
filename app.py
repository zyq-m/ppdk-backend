from datetime import timedelta
from flask import Flask, send_from_directory
from routes import auth, ppdk, admin_ppdk, pelatih, setup, assessment
from extensions import db, f_bcrypt, cors, jwt
from CONSTANT import UPLOAD_FOLDER

app = Flask(__name__)

app.config.from_prefixed_env()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/ppdk_dev3"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_VERIFY_SUB"] = False  # Disable sub validation
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)
jwt.init_app(app)
f_bcrypt.init_app(app)
cors.init_app(app)

app.register_blueprint(auth.bp)
app.register_blueprint(ppdk.bp)
app.register_blueprint(admin_ppdk.bp)
app.register_blueprint(pelatih.bp)
app.register_blueprint(setup.bp)
app.register_blueprint(assessment.bp)


@app.route("/images/<string:name>")
def serve(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    app.run(debug=True)
