import logging
from http import HTTPStatus
from flask import Flask, jsonify, request
from switchbot.domain import commands
from switchbot.service_layer.handlers import InvalidSrcServer
from switchbot import bootstrap, views

logger = logging.getLogger(__name__)
app = Flask(__name__)
bus = bootstrap.bootstrap()


@app.route('/fulfillment', method=['POST'])
def fulfillment():
    raise NotImplementedError


@app.route('/state', methods=['POST'])
def report_state():
    try:
        cmd = commands.ReportState(state=request.json)
        bus.handle(cmd)
        return jsonify({}), HTTPStatus.OK
    except InvalidSrcServer:
        return jsonify({}), HTTPStatus.UNAUTHORIZED


if __name__ == '__main__':
    app.run(debug=True)
