from flask import Flask, render_template, request

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from datetime import datetime
import json
app = Flask(__name__)

engine = create_engine('sqlite:///all_to_the_bottom.db', echo=True)
session = sessionmaker(bind=engine)()


@app.route('/')
def hello_world():
    return render_template('main.html')


@app.route('/getCountryQueries.html', methods=['GET'])
def get_country_queries():
    s = session.execute("select country from actions;")
    data = [record[0] for record in s]
    session.close()
    print(data[:10])
    mp = dict()
    for x in data:
        if x in mp:
            mp[x] += 1
        else:
            mp[x] = 1
    list_country_queries = sorted(mp.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    return json.dumps(list_country_queries)


@app.route('/queriesByCountryAndCategory.html', methods=['POST'])
def queries_by_country_and_category():
    category = request.data.decode("utf-8")
    s = session.execute('select country from actions where category="{}";'.format(category))
    data = [record[0] for record in s]
    session.close()
    print(len(data))
    print(data[:10])
    mp = dict()
    for x in data:
        if x in mp:
            mp[x] += 1
        else:
            mp[x] = 1
    print(len(mp))
    print(mp)
    list_country_queries = sorted(mp.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    print(list_country_queries[:3])
    return json.dumps(list_country_queries)


@app.route('/queriesByDaytimeAndCategory.html', methods=['POST'])
def queries_by_daytime_and_category():
    category = request.data.decode("utf-8")
    s = session.execute('select date from actions where category="{}";'.format(category))
    data = [datetime.strptime(record[0],'%Y-%m-%d_%H:%M:%S') for record in s]
    session.close()
    day_time = {'night': 0, 'morning': 0, 'day': 0, 'evening': 0}
    for x in data:
        if 0 <= x.hour < 6:
            day_time['night'] += 1
        elif x.hour < 12:
            day_time['morning'] += 1
        elif x.hour < 18:
            day_time['day'] += 1
        else:
            day_time['evening'] += 1
    return json.dumps(day_time)


@app.route('/queriesPerHour.html', methods=['GET'])
def queries_per_hour():
    return '4'


@app.route('/categoryWithAnotherCategories.html', methods=['POST'])
def category_with_another_categories():
    category = request.data.decode("utf-8")
    #s = session.execute('select date from actions where category="{}";'.format(category))
    return '5'


if __name__ == '__main__':
    app.run()
