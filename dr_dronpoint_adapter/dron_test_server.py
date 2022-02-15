"""
Simple test server for receiving notification about alarm objects.
"""

from flask import Flask, request, jsonify
import datetime


app = Flask(__name__)


# list of events
alarms = list()


@app.route('/alarm_list/')
def alarm_list():
    """Route for debugging - view all received alarms"""
    return jsonify(alarms)


@app.route('/alarm_notification/')
def alarm_notification():
    """Route for receive notification about alarm"""

    try:
        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
        class_id = int(request.args['class'])

    except ValueError:
        return 'lat and lon variables must be float, class is int'

    except KeyError:
        return 'request must contain class, lat and lon variables'

    alarms.append({'class': class_id, 'timestamp': datetime.datetime.now(), 'lat': lat, 'lon': lon})

    return f'flight to {lat} {lon}'


if __name__ == '__main__':
    # start server in a localhost
    app.run(host='127.0.0.1', port=50411, debug=True)
