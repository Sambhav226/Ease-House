from flask import Flask
from flask_security import SQLAlchemyUserDatastore, Security, auth_required, current_user, hash_password
#from cache import cache
from models import db, Role, User
from api import api
# from werkzeug.security import generate_password_hash
from flask_cors import CORS
from cache import cache
from task import daily_reminder,monthly_reminder
import worker
import uuid
#redis insight app to check caching

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kjwfahishuodhjwq'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization'
app.config['SECURITY_TOKEN_AUTHENTICATION_BEAMER'] = 'Bearer'

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/2'
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 100

cache.init_app(app)

api.init_app(app)
db.init_app(app)

CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)

celery = worker.celery
app.app_context().push()

celery.conf.update(
     broker_url='redis://localhost:6379/1',
     result_backend='redis://localhost:6379/2'
 )

celery.Task = worker.ContextTask
app.app_context().push()

# Return the app without pushing the context here
# app.app_context().push()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Use app context here to run queries and make changes to the database
with app.app_context():
    db.create_all()
    for role_name in ['admin', 'consumer', 'serviceprovider']:
        if not Role.query.filter_by(name=role_name).first():
            user_datastore.create_role(name=role_name)

    if not User.query.filter_by(email='admin@gmail.com').first():
        user_datastore.create_user(username='admin', email='admin@gmail.com', password=hash_password('admin'),
                                   fs_uniquifier=str(uuid.uuid4()), roles=['admin'])
    db.session.commit()

@celery.on_after_configure.connect
def celery_job(sender, **kwargs):
    sender.add_periodic_task(10.0,monthly_reminder.s())
    sender.add_periodic_task(10.0,daily_reminder.s())
    # pass
    # sender.add_periodic_task(

if __name__ == '__main__':
    app.run(port=5050, debug=True)
