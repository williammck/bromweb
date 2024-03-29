from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
import redis

from blueprints.api import api

blueprint = Blueprint('id', __name__, url_prefix='/id')
r = redis.StrictRedis(host='localhost', port=6379, db=0)


@blueprint.route('/auth')
def auth():
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For']
    else:
        ip = request.remote_addr

    minecraft = check_authenticated_ip(ip)
    if minecraft:
        r.delete('brom:id:mc_auth:' + ip)

        session['minecraft_uuid'] = minecraft['uuid']
        session['minecraft_username'] = minecraft['display_name']
        session['minecraft_ip'] = minecraft['ip_address']

        redirect_url = session.pop('mc_auth_callback_url', None)
        return redirect(redirect_url)

    else:
        return render_template('id/auth.html', ip=ip)


def mc_auth(callback_url):
    session['mc_auth_callback_url'] = callback_url
    return redirect(url_for('id.auth'))


def check_authenticated_ip(ip):
    info = r.hgetall('brom:id:mc_auth:' + ip)

    return info


class MinecraftAuthentication(Resource):
    def get(self):
        if 'X-Forwarded-For' in request.headers:
            ip = request.headers['X-Forwarded-For']
        else:
            ip = request.remote_addr
        result = check_authenticated_ip(ip)

        return {'verified': bool(result)}

api.add_resource(MinecraftAuthentication, '/id/auth')
