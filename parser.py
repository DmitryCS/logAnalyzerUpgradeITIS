from datetime import datetime
import re
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
import geoip2.database
import geoip2.errors
from sqlalchemy_utils.functions import drop_database


reader = geoip2.database.Reader('GeoLite2-Country.mmdb')

engine = create_engine('sqlite:///all_to_the_bottom.db', echo=True)
drop_database(engine.url)
Base = declarative_base()


class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    ip = Column(String(120))
    country = Column(String(128))
    date = Column(String(128))
    category = Column(String(128))
    product = Column(String(128))
    parameter1 = Column(String(128))
    parameter2 = Column(String(128))
    parameter3 = Column(String(128))

    def __init__(self, ip='', country='', date='', category='', product='', parameter1='', parameter2='', parameter3=''):
        self.ip = ip
        self.country = country
        self.date = date
        self.category = category
        self.product = product
        self.parameter1 = parameter1
        self.parameter2 = parameter2
        self.parameter3 = parameter3

    def __repr__(self):
        return '<ip %s, country %s>' % (self.ip, self.country)


Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()


#  Определение страны по ip-адресу
def get_country_by_ip(ip_):
    try:
        country_ = reader.country(ip_).country.name
    except geoip2.errors.AddressNotFoundError:
        #  print('IP: {} is not in the GeoLite2-Country database'.format(ip))
        country_ = 'None'
    return str(country_)


# dates = []
# ips = []
# ipp = set()

with open("logs.txt") as f:
    for line in f:
        act = Action()
        date = re.search(r'\d+-\d+-\d+', line).group()
        time = re.search(r'\d+:\d+:\d+', line).group()
        full_date = date+'_'+time
        #dates.append(datetime.strptime(full_date, '%Y-%m-%d_%H:%M:%S'))
        ip = re.search(r'\d+\.\d+\.\d+\.\d+', line).group()
        #ipp.add(ip)
        #ips.append(ip)
        action = re.search(r'bottom.com/(.*)', line).group(1)
        country = get_country_by_ip(ip)
        act.ip = ip
        act.country = country
        act.date = full_date
        if action.startswith('pay'):
            user_id, cart_id = re.search(r'user_id=(\d+)&cart_id=(\d+)', action).groups()
            act.parameter1 = user_id
            act.parameter2 = cart_id
            #print(user_id,cart_id)
        elif action.startswith('cart'):
            goods_id, amount, cart_id = re.search(r'goods_id=(\d+)&amount=(\d+)&cart_id=(\d+)', action).groups()
            act.parameter1 = goods_id
            act.parameter2 = amount
            act.parameter3 = cart_id
            #print(goods_id, amount, cart_id)
        elif action.startswith('success_pay'):
            success_pay_number = re.search(r'success_pay_(\d+)', action).group(1)
            act.parameter1 = success_pay_number
            #print(success_pay_number)
        elif action.count('/') is 0:
            act.category = '/'
        elif action.count('/') is 1:
            section = action[:-1]
            act.category = section
            #print(section)
        elif action.count('/') is 2:
            section, product = re.search(r'(\w+)/(\w+)', action).groups()
            act.category = section
            act.product = product
            #print(section, product)

        engine.echo = False
        session.add(act)
        session.commit()
        session.close()
