#!usr/bin/python
# coding=utf-8

from flask import *
import urllib2
import time
import datetime
import xlrd
import xlwt
from xlutils.copy import copy

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
        urllib2.urlopen(self.openurl).read()
        # pass

    def close(self):
        urllib2.urlopen(self.closeurl).read()
        # pass

# 填入车位上的二维码的id、URL
carlist = [CarportState('001002', 'http://xxx.xxx.xxx.xxx:xxxx/open', 'http://xxx.xxx.xxx.xxx:xxxx/close')]

rb_data = xlrd.open_workbook('DataBase.xls')
count_data = int(rb_data.sheet_by_index(0).cell(0, 1).value)
wb_data = copy(rb_data)
ws_data = wb_data.get_sheet(0)
print '目前数据库中共有%d条数据' % count_data


def get_carport(id):
    for car in carlist:
        if car.id == id:
            return car
        else:
            return None


def record(str_time, str_id, str_action, str_money, str_info):
    global count_data
    count_data += 1
    str_result = u'%s :第%s号车位,%s，费用%s, %s' % (str_time, str_id, str_action, str_money, str_info)
    ws_data.write(0, 1, count_data)
    ws_data.write(count_data + 2, 0, str_time)
    ws_data.write(count_data + 2, 1, str_id)
    ws_data.write(count_data + 2, 2, str_action)
    ws_data.write(count_data + 2, 3, str_money)
    ws_data.write(count_data + 2, 4, str_info)
    wb_data.save('DataBase.xls')
    print str_result


@app.route(APIURL + '/enter_car', methods=['POST'])
def enter_car():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None:
        result = {'result': 'failed'}
    else:
        result = {'result': 'success'}
        carport.start_time = time.time()

        str_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        str_id = carport.id
        str_action = u'车辆进入'
        str_money = u'0.00元'
        str_info = u'进入前15分钟免费停车时间'
        record(str_time, str_id, str_action, str_money, str_info)

    return make_response(jsonify(result), 200)


@app.route(APIURL + '/comfir_car', methods=['POST'])
def comfir_car():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None or not carport.is_empty:
        result = {'result': 'failed'}
    else:
        result = {'result': 'success'}
        carport.is_empty = False
        carport.close()

        str_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        str_id = carport.id
        str_action = u'开始收费'
        str_money = u'0.00元'
        str_info = u'阻档杆升起'
        record(str_time, str_id, str_action, str_money, str_info)

    return make_response(jsonify(result), 200)


@app.route(APIURL + '/exit_car', methods=['POST'])
def exit_car():
    data = request.get_data()
    body = json.loads(data)
    id = body['id']
    carport = get_carport(id)
    if carport is None or carport.is_empty:
        result = {'result': 'failed'}
    else:
        result = {'result': 'success'}
        carport.is_empty = True
        carport.open()
        stopTime = int(time.time() - carport.start_time)
        stopMoney = ((stopTime/60/30) + 1)*5

        carport.close()

        str_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        str_id = carport.id
        str_action = u'完成付款'
        str_money = u'%0.2f元' % stopMoney
        str_info = u'阻档杆降下，停车时长%d秒' % stopTime
        record(str_time, str_id, str_action, str_money, str_info)

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
    import logging
    logging.basicConfig(level=logging.FATAL)
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
