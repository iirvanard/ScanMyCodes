from app import app
from app.controllers.about.main import about
from app.controllers.dashboard.main import dashboard 


# Definisikan rute-rute aplikasi di sini
app.add_url_rule("/", view_func=about)
app.add_url_rule("/about", view_func=dashboard)

