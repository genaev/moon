import numpy as np
import pandas as pd
#from tpot import TPOTClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, classification_report
import xgboost as xgb
from hyperopt import hp
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from sklearn.metrics import log_loss
from sklearn.metrics import precision_score
from sklearn.metrics import cohen_kappa_score
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-x", "--X",  required=True, help="input X file")
parser.add_argument("-y", "--Y",  required=True, help="input Y file")
args = parser.parse_args()

X_file = args.X
Y_file = args.Y

# other imports, custom code, load data, define model...

#X_file = "F_N30L50W10.csv"
#Y_file = "Y_N30L50W10.csv"
#Best params= {'colsample_bytree': 0.35000000000000003, 'gamma': 0.61, 'max_delta_step': 5.0, 'max_depth': 13.0, 'min_child_weight': 1.0, 'scale_pos_weight': 2.0500000000000003, 'subsample': 0.5}

#X_file = "F_N30L30W15.csv"
#Y_file = "Y_N30L30W15.csv"
#Best params= {'colsample_bytree': 0.6000000000000001, 'gamma': 0.71, 'max_delta_step': 9.0, 'max_depth': 13.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9500000000000002, 'subsample': 0.55}

#X_file = "F_N30L30W15.nonorm.csv"
#Y_file = "Y_N30L30W15.nonorm.csv"
#Best params= {'colsample_bytree': 0.75, 'gamma': 0.53, 'max_delta_step': 7.0, 'max_depth': 8.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9500000000000002, 'subsample': 0.5}
#with cal events p=0.57 f1=0.79 Best params= {'colsample_bytree': 0.30000000000000004, 'gamma': 0.6900000000000001, 'max_delta_step': 2.0, 'max_depth': 14.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 0.8}

#X_file = "F_N30L50W10.nonorm.csv"
#Y_file = "Y_N30L50W10.csv"
#no cal events p=0.61 f1=0.79 Best params= {'colsample_bytree': 1.0, 'gamma': 0.72, 'max_delta_step': 4.0, 'max_depth': 14.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 0.55}
#with cal events p=0.63 f1=0.80 Best params=  {'colsample_bytree': 0.75, 'gamma': 0.89, 'max_delta_step': 9.0, 'max_depth': 13.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 0.8}
#with all new traits p=0.68 f1=0.83 Best params{'colsample_bytree': 0.5, 'gamma': 0.61, 'max_delta_step': 4.0, 'max_depth': 14.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 1.0}

#X_file = "F_N30L70W10.csv"
#Y_file = "Y_N30L70W10.csv"
#with all new traits p=0.67 f1=0.82 best_params= {'colsample_bytree': 0.5, 'gamma': 0.61, 'max_delta_step': 4.0, 'max_depth': 14.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 1.0}

#X_file = "F_N30L90W10.csv"
#Y_file = "Y_N30L90W10.csv"
#with all new traits p=0.61 f1=0.82 best_params= {'colsample_bytree': 0.5, 'gamma': 0.61, 'max_delta_step': 4.0, 'max_depth': 14.0, 'min_child_weight': 1.0, 'scale_pos_weight': 1.9000000000000001, 'subsample': 1.0}

trh = 2


X = pd.read_csv(X_file,index_col='id').sort_index()
Y = pd.read_csv(Y_file,index_col='id').sort_index()
Y['y'] = Y.y.apply(lambda x: 1 if x >= trh else 0)

y_skip = ['has_reddit','predicted','start','end','y']
for col in Y.columns.values:
  if not col in y_skip:
    X[col] = Y[col] 

X_train, X_test, y_train, y_test = train_test_split(X, Y.y, test_size=0.33, random_state=17)
ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1)
print ('ratio=',ratio)

#tpot = TPOTClassifier(verbosity=2, population_size=100, offspring_size=100, generations=100, n_jobs=20, scoring='neg_log_loss', cv=5)
#time = 20*60
#tpot = TPOTClassifier(verbosity=2, max_time_mins=time, scoring='neg_log_loss', n_jobs=20, cv=5)
#tpot.fit(X_train, y_train)
#tpot.export('M_N30L50W10.py')

i = 0

def score(params):
    global i
    i = i + 1
    #print(i,"Training with params:")
    #print(params)
    params['max_depth'] = int(params['max_depth'])
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dvalid = xgb.DMatrix(X_test, label=y_test)
    model = xgb.train(params, dtrain, params['num_round'])
    predictions = model.predict(dvalid).reshape((X_test.shape[0], 1))
    #score = log_loss(y_test, predictions)
    score = 1-precision_score(y_test,
                              np.apply_along_axis(lambda x: np.where(x > 0.5, 1, 0), 0, predictions)
                             )+log_loss(y_test, predictions)
    score_new = -cohen_kappa_score(y_test,np.apply_along_axis(lambda x: np.where(x > 0.5, 1, 0), 0, predictions))
    #print("\tScore {0}\n\n".format(score))
    return {'loss': score_new, 'status': STATUS_OK}

def optimize(trials):
    space = {
             'num_round': 100,
             'learning_rate': 0.01,
             'max_depth': hp.quniform('max_depth', 6, 20, 1),
             'min_child_weight': hp.quniform('min_child_weight', 1, 6, 1),
             'subsample': hp.quniform('subsample', 0.7, 1, 0.05),
             'gamma': hp.quniform('gamma', 0.5, 1, 0.01),
             'colsample_bytree': hp.quniform('colsample_bytree', 0.3, 1, 0.05),
             'eval_metric': 'error',
             'objective': 'binary:logistic',
             'max_delta_step': hp.quniform('max_delta_step', 0, 10, 1),
             'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 3, 0.05),
             'nthread' : 26,
             'silent' : 1
             }
    
    best = fmin(score, space, algo=tpe.suggest, trials=trials, max_evals=1000)
    return best

trials = Trials()
best_params = optimize(trials)
print('Best params=',best_params)
best_params['learning_rate'] = 0.001
best_params['max_depth'] = int(best_params['max_depth'])
best_params['eval_metric'] = 'error'
best_params['objective'] = 'binary:logistic'
best_params['nthread'] = 20
best_params['silent'] = 1

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test)

xgbCvResult = xgb.cv(best_params, dtrain, 
                      num_boost_round=2000,
                      nfold=5, early_stopping_rounds=50)

best_num_round = np.argmin(xgbCvResult['test-error-mean'])

print("best_num_round=",best_num_round)

bestXgb = xgb.train(best_params, dtrain, num_boost_round=best_num_round)

xgboost_predict_proba = bestXgb.predict(dtest)
y_test_preds = (xgboost_predict_proba > 0.5).astype('int')
report = classification_report(y_test, y_test_preds)
print(report)
