from flask import Flask
from flask_cors import CORS
from api.test import test_api
from api.create_pdf import create_pdf

app = Flask(__name__)
CORS(app)

app.register_blueprint(test_api)
app.register_blueprint(create_pdf)

if __name__ == '__main__':
    app.run(debug=True)
