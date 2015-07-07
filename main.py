import os

from flask import Flask
import sqlite3 as lite
import pandas as pd
from flask import render_template
import json
from sklearn.externals import joblib
from collections import OrderedDict

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
	con = lite.connect('test.db')
	if "DATABASE_URL" in os.environ:
		import psycopg2
		from sqlalchemy import create_engine
		con = create_engine(os.environ["DATABASE_URL"])
	lossProb = pd.read_sql("SELECT * FROM lossprob", con, parse_dates=['Date']).set_index('Date')['LossProb']
	market = pd.read_sql("SELECT * FROM market", con).set_index('Date')['Close']
	inputs = pd.read_sql("SELECT * FROM inputs", con).set_index('Date') * 100
	lossProbDiff = pd.read_sql("SELECT * FROM lossprobdiff", con).set_index('Date') * 100

	#clf = joblib.load('models/model.pkl') 

	return render_template('index.html', 
		market=market.to_json(), 
		lossProb=lossProb.to_json(),
		inputs=OrderedDict(sorted(inputs.to_dict(orient="records")[-1].items(), key=lambda x: int(x[0]))),
		#modelCoeff=dict(zip(inputs.columns.values, clf.coef_[0])),
		lossProbDiff=OrderedDict(sorted(lossProbDiff.to_dict(orient="records")[-1].items(), key=lambda x: int(x[0]))),
		latestDate=str(inputs.index[-1:].values[0])[:10]
		)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')