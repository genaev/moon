import numpy as np
import pandas as pd
import xgboost as xgb
import xgbfir
import ast
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, classification_report

parser = argparse.ArgumentParser()
parser.add_argument("-x", "--X",  required=True, help="input X file")
parser.add_argument("-y", "--Y",  required=True, help="input Y file")
parser.add_argument("-o", "--O",  required=True, help="output file with model")
parser.add_argument("-p", "--P",  required=True, help="model params")
args = parser.parse_args()

X_file = args.X
Y_file = args.Y
model_file= args.O
best_params = ast.literal_eval(args.P)
best_params['learning_rate'] = 0.001
best_params['eval_metric'] = 'error'
best_params['objective'] = 'binary:logistic'
best_params['nthread'] = 8
best_params['silent'] = 1

trh = 2

X = pd.read_csv(X_file,index_col='id').sort_index()
Y = pd.read_csv(Y_file,index_col='id').sort_index()
Y['y'] = Y.y.apply(lambda x: 1 if x >= trh else 0)

y_skip = ['predicted','start','end','y']
for col in Y.columns.values:
  if not col in y_skip:
    X[col] = Y[col]

X_train, X_test, y_train, y_test = train_test_split(X, Y.y, test_size=0.33, random_state=17)
ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1)
print("ratio=",ratio)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test)

xgbCvResult = xgb.cv(best_params, dtrain,
                      num_boost_round=1000,
                      nfold=5, early_stopping_rounds=50)

best_num_round = np.argmin(xgbCvResult['test-error-mean'])

print("best_num_round=",best_num_round)

bestXgb = xgb.train(best_params, dtrain, num_boost_round=best_num_round)

# save model
bestXgb.save_model(model_file)

# dump model
features = list(X_train.columns.values)
bestXgb.feature_names = features # set names for XGBoost booster

outfile = open(model_file+'.fmap', 'w')
for i, feat in enumerate(features):
  outfile.write('{0}\t{1}\tq\n'.format(i, feat))
outfile.close()

bestXgb.dump_model(model_file+'.dump',with_stats=True)

xgbfir.saveXgbFI(bestXgb, feature_names=features, OutputXlsxFile=model_file+'.xlsx')

xgboost_predict_proba = bestXgb.predict(dtest)
y_test_preds = (xgboost_predict_proba > 0.5).astype('int')
report = classification_report(y_test, y_test_preds)
print(report)
