__author__ = 'jmpews'

from flask import Module,request
from proxys.models import Proxy
from flask import render_template

index_module=Module(__name__)

@index_module.route('/')
def index():
    r_type=request.args.get('proxytype','http')
    # proxylist=Proxy.query.all()
    proxylist=Proxy.query.filter_by(type=r_type).limit(1000).all()
    return render_template('index.html',proxylist=proxylist)