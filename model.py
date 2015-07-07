import os
import sqlite3 as lite
import Quandl
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import PolynomialFeatures
from sklearn.externals import joblib


con = lite.connect('test.db')
if "DATABASE_URL" in os.environ:
	import psycopg2
	from sqlalchemy import create_engine
	con = create_engine(os.environ["DATABASE_URL"])

data = Quandl.get("YAHOO/INDEX_GSPC")
mkt = data['Close']

df = pd.DataFrame()
liveDf = pd.DataFrame()
for per in [21, 63, 126, 252, 504, 756]:
    df['%d'%per] = mkt.pct_change(periods=per).shift(periods=65)
    liveDf['%d'%per] = mkt.pct_change(periods=per)
df.dropna(inplace=True)
liveDf.dropna(inplace=True)
yData_raw = mkt.pct_change(periods=63)
yData = yData_raw.apply(lambda x: 1 if x<-0.10 else -1).reindex(index=df.index)

#poly = PolynomialFeatures(degree=2)
#df = pd.DataFrame(poly.fit_transform(df), index=yData.index)

TRAIN_START = '1955-1-1'
TRAIN_END = '2015-6-30'

clf = LogisticRegression(penalty='l2')
clf.fit(df[TRAIN_START:TRAIN_END], yData[TRAIN_START:TRAIN_END])

probs = clf.predict_proba(liveDf[TRAIN_START:])

sellConf = pd.DataFrame(probs, index=yData[TRAIN_START:].index, columns=['No Loss Probability', 'LossProb'])
y = sellConf['LossProb']

lossProbDiff = pd.DataFrame()
for per in [5, 21, 63, 252]:
    lossProbDiff[per] = y.diff(periods=per)

lossProbDiff[-252:].to_sql('lossprobdiff', con, if_exists='replace')
y.to_sql('lossprob', con, if_exists='replace')
mkt.to_sql('market', con, if_exists='replace')
liveDf[-1:].to_sql('inputs', con, if_exists='replace')

print clf.intercept_
print dict(zip(liveDf.columns.values, clf.coef_[0]))
print lossProbDiff[-252:]
#joblib.dump(clf, 'models/model.pkl') 