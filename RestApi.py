import json
from cosmosclient import CosmosClient as cc
from flask import Flask, jsonify, request, render_template
from flask_restful import Resource, Api
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_restful_swagger import swagger

app = Flask(__name__)
app.config["SWAGGER"] = {"title":"Intelligent-Web-Protoype", "uiversion":2}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint":"apispec_1",
            "route":"/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path":"/flagger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
}

swagger = Swagger(app, config=swagger_config)

@app.route("/")
def index():
    # console.log("here")
    return render_template("htmlfile.html")

@app.route("/allItems", methods=['GET'])
@swag_from("swagger_config.yml")
def get_items():
    return jsonify(cc.get_all_items())


@app.route("/addItem", methods=['GET','POST'])
def add_item():
    if(request.method == 'POST'):
        item = request.get_json()
        try:
            cc.create_product(item)
            return "Item with id {0} added successfully".format(item['id']), 201
        except:
            return "Item with id {0} already exists in the database".format(item['id']), 404

if __name__ == '__main__':
    app.run(debug=True)