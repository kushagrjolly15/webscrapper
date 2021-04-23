import json
from flask import Flask, jsonify, request, render_template
import cosmosclient.CosmosClient as cc





app = Flask(__name__)


@app.route("/")
def index():
   
    return render_template("htmlfile.html")

@app.route("/product", methods=['GET'])
def product_details():
    id = request.args['id']
    json_result = cc.get_item_by_id(id)
    size_json = json.loads(json_result["size_chart"])
    keys = size_json.keys()
    size_table = {}
    for key,values in size_json.items():
        dic = {}
        for j in keys:
            dic[j] = size_json[j][key]
        size_table[key] = dic
    json_result["size_chart"] = size_table
    return jsonify(json_result)

if __name__ == '__main__':
    app.run(debug=True)