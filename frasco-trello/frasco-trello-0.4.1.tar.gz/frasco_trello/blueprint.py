from frasco import Blueprint, redirect, url_for, request, flash
from werkzeug import url_quote


def create_blueprint(app):
    bp = Blueprint("trello_login", __name__)

    feature = app.features.trello
    users = app.features.users

    @bp.route('/login/trello')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        return feature.api.authorize(callback_url,
            name=feature.options["app_name"],
            scope=feature.options["scope"],
            expiration=feature.options["expiration"])

    @bp.route('/login/trello/callback')
    def callback():
        resp = feature.api.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        me = feature.api.get('members/me',
            headers={'Accept': 'application/json'},
            data={'key': feature.options['api_key'], 'token': resp['oauth_token']},
            token=resp['oauth_token'])

        attrs = {"trello_oauth_token": resp['oauth_token'],
                 "trello_oauth_token_secret": resp['oauth_token_secret'],
                 "trello_user_id": me.data['id'],
                 "trello_username": me.data['username']}
        defaults = {}
        if feature.options["use_username"] and users.options['email_column'] != users.options['username_column']:
            defaults[users.options["username_column"]] = me.data['username']

        return users.oauth_login("trello", "trello_user_id", me.data['id'], attrs, defaults)

    return bp