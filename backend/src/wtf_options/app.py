from flask import Flask
from flask_cors import CORS
from .controllers.options_controller import options_blueprint
from .utils.log_util import log

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing to allow the frontend to communicate with this backend
CORS(app)

app.register_blueprint(options_blueprint)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
