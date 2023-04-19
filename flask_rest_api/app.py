from flask import Flask, Response, request, jsonify
from flask_restful import Resource, Api
from google_calendar_api import get_today_events

app = Flask(__name__)
api = Api(app)


@app.route('/api/v1/gcal_assistant', methods=['GET'])
def show_today_events():
    return Response(get_today_events(), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)