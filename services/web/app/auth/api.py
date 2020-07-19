from . import auth

from .views import basic_user_accounts_schema
from .models import UserAccount

@auth.route("/api")
def api_home():
    return {"results": UserAccount.query.all()}