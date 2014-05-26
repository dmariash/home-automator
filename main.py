import yaml
import rawsender
import plugsender
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth


app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    if username == 'dan':
        return 'dan'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 401)


plugs_yaml = './plugs.yaml'

plug_fields = {
    'name': fields.String,
    'channel': fields.Integer,
    'button': fields.Integer,
    'uri': fields.Url('plug', absolute=True)
}


class PlugListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, required = True, help='No plug name provided', location = 'json')
        self.reqparse.add_argument('channel', type = int, required = True, help='No channel provided', location = 'json')
        self.reqparse.add_argument('button', type = int, required = True, help='No button provided', location = 'json')

    def get(self):

        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        return { 'plugs': map(lambda p: marshal(p, plug_fields), plugs) }

    @auth.login_required
    def post(self):

        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        args = self.reqparse.parse_args()
        name = args['name']
        channel = args['channel']
        button = args['button']
        plug = filter(lambda p: p['name'] == name, plugs)
        if len(plug) != 0:
            abort(403)
        plug = filter(lambda p: p['channel'] == channel and p['button'] == button, plugs)
        if len(plug) != 0:
            abort(403)
        plug = {
            'name': name,
            'channel': channel,
            'button': button,
        }
        plugs.append(plug)

        with open(plugs_yaml, 'w') as file:
            file.write(yaml.dump(plugs))

        return { 'plug': marshal(plug, plug_fields) }, 201


class PlugAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('channel', type = int, location = 'json')
        self.reqparse.add_argument('button', type = int, location = 'json')

    def get(self, name):
        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        plug = filter(lambda p: p['name'] == name, plugs)
        if len(plug) == 0:
            abort(404)
        return { 'plug': marshal(plug[0], plug_fields) }

    @auth.login_required
    def put(self, name):
        # TODO: Make sure that no other plug has the same channel and button!!

        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        plug = filter(lambda p: p['name'] == name, plugs)
        if len(plug) == 0:
            abort(404)
        args = self.reqparse.parse_args()
        plug[0]['name'] = request.json.get('name', name)
        plug[0]['channel'] = request.json['channel']
        plug[0]['button'] = request.json['button']

        with open(plugs_yaml, 'w') as file:
            file.write(yaml.dump(plugs))

        return { 'plug': marshal(plug, plug_fields) }

    @auth.login_required
    def delete(self, name):

        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        plug = filter(lambda p: p['name'] == name, plugs)
        if len(plug) == 0:
            abort(404)
        plugs.remove(plug[0])

        with open(plugs_yaml, 'w') as file:
            file.write(yaml.dump(plugs))

        return { 'result': True }


class SendPlugAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type = str, location = 'json')
        self.reqparse.add_argument('state', type = str, location = 'json')
        self.reqparse.add_argument('pin', type = int, location = 'json', required=False, default=0)

    def post(self):

        with open(plugs_yaml,'r') as file:
            plugs = yaml.load(file)

        args = self.reqparse.parse_args()
        print args
        plug = filter(lambda p: p['name'] == args['name'], plugs)
        if len(plug) == 0:
            abort(404)
        plug = plug[0]
        try:
            plugsender.send(args.get('pin', 0), plug['channel'], plug['button'], args['state'])
        except Exception:
            abort(400)
        else:
            return { 'result': True }


class SendRawAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('code', type = str, location = 'json')
        self.reqparse.add_argument('pin', type = int, location = 'json')

    def post(self):
        args = self.reqparse.parse_args()
        print args.get('pin')
        try:
            rawsender.send(args.get('pin', 0), args['code'])
        except Exception:
            abort(400)
        else:
            return { 'result': True }


api.add_resource(PlugListAPI, '/plugs', endpoint = 'plugs')
api.add_resource(PlugAPI, '/plugs/<string:name>', endpoint = 'plug')
api.add_resource(SendPlugAPI, '/sendplug', endpoint = 'sendplug')
api.add_resource(SendRawAPI, '/sendraw', endpoint = 'sendraw')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug = True)