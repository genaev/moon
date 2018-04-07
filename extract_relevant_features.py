import pandas as pd
from tsfresh import extract_relevant_features
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-x", "--X",  required=True, help="input X file")
parser.add_argument("-y", "--Y",  required=True, help="input Y file")
parser.add_argument("-o", "--O",  required=True, help="output file")
args = parser.parse_args()



X_file = args.X
Y_file = args.Y
out_csv= args.O
trh = 2

print (X_file,Y_file,out_csv)
#exit(0)

y = pd.read_csv(Y_file)
#y = y.drop(['start', 'end'], axis=1)
y = y.set_index('id')
y['y'] = y.y.apply(lambda x: True if x >= trh else False)

x = pd.read_csv(X_file)
print("cells with NaN ",x.isnull().sum().sum())
print("unic ids ",x.id.nunique())
#x = x.fillna(method='ffill').fillna(method='bfill').fillna(0)
#x.dropna(axis=1, inplace=True)
#print (y.y)

features_filtered_direct = extract_relevant_features(x, y.y, column_id='id', column_sort='date', n_jobs=20)
features_filtered_direct.to_csv(out_csv)
