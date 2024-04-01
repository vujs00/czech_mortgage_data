# -*- coding: utf-8 -*-
"""
@author: Stevan Vujcic

"""

#------------------------------------------------------------#
# STEP 1: setup                                              #
#------------------------------------------------------------#

df = pd.read_parquet(interim_library_path + r'\01-1_-_df.parquet')

train_export_path = interim_library_path + r'\01-2_-_df_train.parquet'
test_export_path = interim_library_path + r'\01-2_-_df_test.parquet'

#------------------------------------------------------------#
# STEP 2: split                                              #
#------------------------------------------------------------#

X = df.loc[:, df.columns != 'default_event_flg']
y = df.loc[:, 'default_event_flg']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3,
                                                    random_state = set_seed)

y_train = pd.DataFrame(y_train)
y_test = pd.DataFrame(y_test)

df_train = y_train.join(X_train, how = 'left')
df_test = y_test.join(X_test, how = 'left')

df_train.to_parquet(train_export_path)
df_test.to_parquet(test_export_path)

del df, train_export_path, test_export_path, X, y, y_train, y_test, X_test
del X_train, df_train, df_test
