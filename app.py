
from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory
from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.bcrypt import *
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.base import MenuLink
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
import os.path as op
from decorators import async
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Shell, Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, LoginForm, \
        RegisterForm, ForgotPasswordForm, current_user, login_required, url_for_security
from flask.ext.security.forms import ChangePasswordForm

# Create app
app = Flask(__name__)
app.config.from_object('config.config')
app.config.from_object('env.env') #overwrites config.config for production server
app.config.from_object('env.email') #overwrites config.config for production server
install_dir = op.split(op.realpath(__file__))[0]

# Setup mail extension
mail = Mail(app)

# Setup babel
babel = Babel(app)

# useful for a separate production servers
def my_app(environ, start_response): 
    path = environ["PATH_INFO"]  
    if path == "/":  
        return app(environ, start_response)     
    else:  
        return app(environ, start_response) 

@babel.localeselector
def get_locale():
    override = request.args.get('lang')

    if override:
        session['lang'] = override

    rv = session.get('lang', 'en')
    return rv

@app.context_processor
def inject_userForms():
    return dict(login_form=LoginForm(), register_user_form=RegisterForm(), \
        forgot_password_form=ForgotPasswordForm(), change_password_form=ChangePasswordForm())

# Create database connection object
def _make_context():
    return dict(app=app, mail=mail, db=db, babel=babel, security=security, admin=admin)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context))

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return '<User id=%s email=%s>' % (self.id, self.email)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@async
def send_security_email(msg):
    with app.app_context():
       mail.send(msg)

@security.send_mail_task
def async_security_email(msg):
    send_security_email(msg)

# db.create_all()

# Views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/custom/<path:filename>')
def custom(filename):
    return send_from_directory(op.join(install_dir, app.config['CUSTOM_STATIC_PATH']), filename)

@app.route('/profile')
def profile():
    if current_user.is_authenticated():
        return render_template('profile.html')
    else:
        return redirect(url_for_security('login'))
        
admin = Admin(app)

# Admin Views
class MyModelView(ModelView):
    def is_accessible(self):
        return True  # remove
        # return current_user.has_role('admin')  # uncomment to lock down admin

class MyFileView(FileAdmin):
    def is_accessible(self):
        return True  # remove
        # return current_user.has_role('admin')  # uncomment to lock down admin

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(MyFileView(path, '/static/', name='Static Files'))
admin.add_link(MenuLink(name='Back Home', url='/'))

if __name__ == '__main__':
    manager.run()
