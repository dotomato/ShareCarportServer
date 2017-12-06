#!usr/bin/python
# coding=utf-8

from flask import *
import urllib2
import time

app = Flask(__name__)

VERSION = 'v0.01'
APIURL = '/api/' + VERSION


class CarportState:

    def __init__(self, id, openurl, closeurl):
        self.id = id
        self.is_empty = True
        self.openurl = openurl
        self.closeurl = closeurl
        self.start_time = -1

    def open(self):
        # print 'open'
        urllib2.urlopen(self.openurl).read()

    def close(self):
        # print 'close'
        urllib2.urlopen(self.closeurl).read()

# 填入车位上的二维码的id、URL
carlist = [CarportState('111', 'http://xxx.xxx.xxx.xxx:5001/open', 'http://xxx.xxx.xxx.xxx:5001/close')]


def get_carport(id):
    for car in carlist:
        if car.id == id:
            return car
        else:
            return None


@app.route(APIURL + '/enter_car', methods=['POST'])
def enter_car():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None or not carport.is_empty:
        result = {'result': 'failed'}
    else:
        result = {'result': 'success'}
        carport.is_empty = False
        carport.start_time = time.time()
        carport.close()
        print 'carport has closed ,id=%s' % id
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/exit_car', methods=['POST'])
def exit_car():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None:
        result = {'result': 'failed'}
    else:
        result = {'result': 'success'}
        carport.is_empty = True
        carport.open()
        print 'carport has opened ,id=%s' % id
    return make_response(jsonify(result), 200)


@app.route(APIURL + '/get_time', methods=['POST'])
def get_time():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None or carport.is_empty:
        result = {'result': 'failed'}
    else:
        t = long(time.time() - carport.start_time)
        result = {'result': 'success', 'time': t}
    return make_response(jsonify(result), 200)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
