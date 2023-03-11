import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import joblib


df = pd.read_csv('get_around_pricing_project.csv')

# set rare titles if model keys appear less then 5 times 
model_key = dict(df.model_key.groupby(df.model_key).count().sort_values(ascending=False))
rare_titles = [model for model, count in model_key.items() if count < 5 ]

# replace rare titles 
df['model_key'] = df['model_key'].replace(rare_titles, 'Rare')
# drop useless columns
df = df.drop(["Unnamed: 0"], axis=1)

# split target and features variables
target_variable = "rental_price_per_day"
X = df.drop(target_variable, axis = 1)
Y = df.loc[:,target_variable]

# separate numeric and categorical features
numeric_features = [1, 2]
categorical_features = [0,3,4,8,6,7,8,9,10,11,12]

# Train & Test split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

# preprocessing
numeric_transformer = Pipeline(steps=[('scaler', StandardScaler())])
categorical_transformer = Pipeline(steps = [('encoder', OneHotEncoder(handle_unknown = 'ignore'))])
preprocessor = ColumnTransformer(transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)])

# fit it on X train and X test
X_train = preprocessor.fit_transform(X_train)

X_test = preprocessor.transform(X_test)

# Train model
print("Train model...")
model = LinearRegression()
model.fit(X_train, Y_train)
print("...Done.")

# save the model and the preprocessor to disk
filename = 'finalized_model.joblib'
joblib.dump(model, open(filename, 'wb'))

joblib.dump(preprocessor, open('preprocessor.joblib', 'wb'))


# load the model from disk
loaded_model = joblib.load(open(filename, 'rb'))
result = loaded_model.score(X_test, Y_test)
print(result)

print("...Done!")