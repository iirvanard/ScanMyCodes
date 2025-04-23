# from app import app
# from app.controllers.about.main import about
# from app.controllers.dashboard.main import dashboard

# # Definisikan rute-rute aplikasi di sini
# app.add_url_rule("/", view_func=about)
# app.add_url_rule("/about", view_func=dashboard)

from .modules.project_detail import project_details
from .modules import dashboard, projects,profile_page
from .modules.auth import auth

from .modules.api import chat_openai
from app import app

app.register_blueprint(dashboard.blueprint)
app.register_blueprint(auth.auth_blueprint)
app.register_blueprint(project_details.blueprint)
app.register_blueprint(projects.blueprint)
app.register_blueprint(chat_openai.blueprint)
app.register_blueprint(profile_page.blueprint)

# app.register_blueprint(user.blueprint)
