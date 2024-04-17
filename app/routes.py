# from app import app
# from app.controllers.about.main import about
# from app.controllers.dashboard.main import dashboard

# # Definisikan rute-rute aplikasi di sini
# app.add_url_rule("/", view_func=about)
# app.add_url_rule("/about", view_func=dashboard)

from .modules import index, project
from .modules.auth import auth
from app import app

app.register_blueprint(index.blueprint)
app.register_blueprint(auth.auth_blueprint)
app.register_blueprint(project.blueprint)
# app.register_blueprint(user.blueprint)
