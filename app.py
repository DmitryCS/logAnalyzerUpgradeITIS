from flask import Flask, render_template, request

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
#import parser

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
    return str(list_country_queries)


@app.route('/queriesByCountryAndCategory.html', methods=['POST'])
def queries_by_country_and_category():
    category = request.data.decode("utf-8")
    s = session.execute('select country from actions where category="{}";'.format(category))
    data = [record[0] for record in s]
    session.close()
    print(len(data))
    print(data[:])
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
    return str(list_country_queries)


if __name__ == '__main__':
    app.run()
