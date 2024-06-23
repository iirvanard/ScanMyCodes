# from app import app
# from app.controllers.about.main import about
# from app.controllers.dashboard.main import dashboard

# # Definisikan rute-rute aplikasi di sini
# app.add_url_rule("/", view_func=about)
# app.add_url_rule("/about", view_func=dashboard)

<<<<<<< HEAD
from .modules import index, project_details, projects
from .modules.auth import auth
=======
<<<<<<< HEAD
from app.controllers import index
>>>>>>> 57a24e6 (before revisi)

from .modules.api import chat_openai
from app import app

app.register_blueprint(index.blueprint)
<<<<<<< HEAD
=======
# app.register_blueprint(goodbye.blueprint)
=======
from .modules import index, project_details, projects
from .modules.auth import auth

from .modules.api import chat_openai
from app import app

app.register_blueprint(index.blueprint)
>>>>>>> 57a24e6 (before revisi)
app.register_blueprint(auth.auth_blueprint)
app.register_blueprint(project_details.blueprint)
app.register_blueprint(projects.blueprint)
app.register_blueprint(chat_openai.blueprint)

<<<<<<< HEAD
=======
>>>>>>> 2fc3767 (before revision)
>>>>>>> 57a24e6 (before revisi)
# app.register_blueprint(user.blueprint)
