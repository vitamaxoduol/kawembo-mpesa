# from mpesa.mpesa_routes import mpesa_routes
# from routes.user_auth import user_auth
# from routes.images import image_routes
# from routes.application_routes import membership_application
# from routes.admin_approvals import admin_approval_routes
# from routes.admin_actions import admin_actions_routes
# from routes.send_code import send_code
# from routes.verify_code import verify_code
# from routes.announcements import announcements
# from routes.user_operations import user_operations
from mpesa.utils import access_authentication
# from mpesa.mpesa import mpesa_route
# from mpesa.stk_push import bind_routes


def register_routes(app, db, server_url, socketio):

    @app.route("/", methods=["GET"])
    def welcome():
        return "Welcome to KAWEBOs API."

    # mpesa_routes(app, db, server_url, socketio)

    # user_auth(app, db, server_url, socketio)

    # image_routes(app, db, server_url)

    # membership_application(app, db, socketio)

    # admin_approval_routes(app, db, socketio)

    # admin_actions_routes(app, db)

    # send_code(app, db)

    # verify_code(app, db)

    # announcements(app, db, socketio)

    # user_operations(app, db)
    
    access_authentication(app, socketio)
    
    # mpesa_route(app)

    # bind_routes(app,socketio)