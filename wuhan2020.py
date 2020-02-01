#-*-coding:utf8-*-
import time
import json
import requests
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.figure
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
plt.rcParams['font.sans-serif'] = ['FangSong']
plt.rcParams['axes.unicode_minus'] = False
cur_dir = os.path.dirname(os.path.realpath(__file__))


def fetch_data(url):
    data = json.loads(requests.get(url=url).json()['data'])
    #print(data)
    return data


def catch_distribution():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_area_counts&callback=&_=%d' % int(time.time())
    raw_data = fetch_data(url)
    data = {}
    for item in raw_data:
        if item['area'] not in data:
            data.update({item['area']:0})
        data[item['area']] += int(item['confirm'])
    return data


def catch_daily(raw_data):
    raw_data.sort(key=lambda x: x['date'])
    date_list = list()
    confirm_list = list()
    suspect_list = list()
    dead_list = list()
    heal_list = list()
    for item in raw_data:
        month, day = item['date'].split('.')
        date_list.append(datetime.strptime('2020-%s-%s' % (month, day), '%Y-%m-%d'))
        confirm_list.append(int(item['confirm']))
        suspect_list.append(int(item['suspect']))
        dead_list.append(int(item['dead']))
        heal_list.append(int(item['heal']))
    return date_list, confirm_list, suspect_list, dead_list, heal_list


def plot_daily(raw_data):
    date_list, confirm_list, suspect_list, dead_list, heal_list = catch_daily(raw_data)
    plt.figure('2019-nCov wuhan2020', facecolor='#f4f4f4', figsize=(10, 8))
    plt.title('2019-nCov plot', fontsize=20)
    plt.plot(date_list, confirm_list, label='confirm')
    plt.plot(date_list, suspect_list, label='suspect')
    plt.plot(date_list, dead_list, label='dead')
    plt.plot(date_list, heal_list, label='heal')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.grid(linestyle=':')
    plt.legend(loc='best')
    plt.savefig(cur_dir + '/2019-nCov-daily.png')
    plt.show()


def plot_distribution():
    data = catch_distribution()
    font = FontProperties(fname=cur_dir + '/res/simsun.ttc')
    lat_min = 0
    lat_max = 60
    lon_min = 70
    lon_max = 140
    handles = [
        matplotlib.patches.Patch(color='#ffaa85', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#ff7b69', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#bf2121', alpha=1, linewidth=0),
        matplotlib.patches.Patch(color='#7f1818', alpha=1, linewidth=0)
    ]
    labels = ['1-9', '10-99', '100-999', '>1000']
    fig = matplotlib.figure.Figure()
    fig.set_size_inches(10, 8)
    axes = fig.add_axes([0.1, 0.12, 0.8, 0.8])
    m = Basemap(llcrnrlon=lon_min, urcrnrlon=lon_max, llcrnrlat=lat_min, urcrnrlat=lat_max, resolution='l', ax=axes)
    m.readshapefile(cur_dir + '/res/china-shapefiles/china', 'province', drawbounds=True)
    m.readshapefile(cur_dir + '/res/china-shapefiles/china_nine_dotted_line', 'section', drawbounds=True)
    m.drawcoastlines(color='black')
    m.drawcountries(color='black')
    m.drawparallels(np.arange(lat_min, lat_max, 10), labels=[1, 0, 0, 1])
    m.drawmeridians(np.arange(lon_min, lon_max, 10), labels=[0, 0, 0, 1])
    for info, shape in zip(m.province_info, m.province):
        pname = info['OWNER'].strip('\x00')
        fcname = info['FCNAME'].strip('\x00')
        if pname != fcname:
            continue
        for key in data.keys():
            if key in pname:
                if data[key] == 0:
                    color = '#f0f0f0'
                elif data[key] < 10:
                    color = '#ffaa85'
                elif data[key] < 100:
                    color = '#ff7f69'
                elif data[key] < 1000:
                    color = '#bf2121'
                else:
                    color = '#7f1818'
                break
        poly = Polygon(shape, facecolor=color, edgecolor=color)
        axes.add_patch(poly)
    axes.legend(handles, labels, bbox_to_anchor=(0.5, -0.11), loc='lower center', ncol=4, prop=font)
    axes.set_title('map for 2019-nCov', fontproperties=font)
    FigureCanvasAgg(fig)
    fig.savefig(cur_dir + '/2019-nCov.png')




if __name__ == '__main__':
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=wuwei_ww_cn_day_counts&callback=&_=%d' % int(time.time() * 1000)
    raw_data = fetch_data(url)
    #data = catch_distribution(raw_data)
    #print(data)
    plot_daily(raw_data)
    plot_distribution()