from datetime import timedelta
from flask import Flask
from routes import auth, ppdk, admin_ppdk, pelatih, setup
from extensions import db, f_bcrypt, cors, jwt

app = Flask(__name__)

app.config.from_prefixed_env()
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/ppdk_dev"
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

db.init_app(app)
jwt.init_app(app)
f_bcrypt.init_app(app)
cors.init_app(app)

app.register_blueprint(auth.bp)
app.register_blueprint(ppdk.bp)
app.register_blueprint(admin_ppdk.bp)
app.register_blueprint(pelatih.bp)
app.register_blueprint(setup.bp)

if __name__ == "__main__":
    app.run(debug=True)
