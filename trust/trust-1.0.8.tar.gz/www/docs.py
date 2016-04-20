import collections
import flask
import json
import markdown
import os
import requests


docs_blueprint = flask.Blueprint(
    "www/docs", __name__,
    template_folder="templates",
    static_folder="static"
)


@docs_blueprint.route("/")
def index():
    app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    global_file = "tests/system/data/data-tests.json"

    with open(os.path.join(app_path, global_file)) as f:
        data = json.load(f)

    illustrations = sorted(
        [c for c
         in data["system-tests"].items()
         if "show-on-site" in c[1]],
        key=lambda t: t[1]["position"]
    )

    with open(os.path.join(app_path, "README.markdown")) as f:
        docs_markdown = f.read()

    return flask.render_template(
        "global.html",
        illustrations=illustrations,
        request=flask.request,
        base_uri=flask.request.url_root[7:],
        documentation=markdown.markdown(docs_markdown)
    )


@docs_blueprint.route("/css")
def css():
    return docs_blueprint.send_static_file("g.min.css")


@docs_blueprint.route("/logo")
def logo():
    return docs_blueprint.send_static_file("trust-logo-top.png")


@docs_blueprint.route("/logo-bottom")
def logo_bottom():
    return docs_blueprint.send_static_file("trust-logo-bottom.png")


@docs_blueprint.route("/proxy", methods=["GET"])
def query_proxy():
    app_url = flask.request.host_url
    query = flask.request.args.get("query", "")
    response = requests.get(
        app_url + "service/" + query + "?response-mode=json&optional=1",
        auth=("William", "demo")
    )

    return (response.text, response.status_code)
