# -*- coding: utf-8 -*-
"""
@author: Stevan Vujcic
"""

#------------------------------------------------------------#
# STEP 1: general imports and paths                          #
#------------------------------------------------------------#

# Data manipulation.
import pandas as pd

# Metrics.
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

# Performance.
from datetime import datetime

# Load dataset.
df0 = pd.read_csv(r'C:\Users\JF13832\Downloads\Thesis\03 Data\01 Source\czech_mortgages_dataset_v2.csv', 
                  decimal = ',',
                  delimiter = '|',
                  encoding = 'cp437')

helper_1 = df0.loc[df0['DefaultEvent'] == 1]
helper_2 = df0.loc[df0['DefaultEvent'] == 0]
helper_2 = helper_2.head(1000)
df0 = pd.concat([helper_1, helper_2])

# Variable name mapping dataset.
variable_mapping0 = pd.read_excel(r'C:\Users\JF13832\Downloads\Thesis\03 Data\01 Source\mapping_tables.xlsx',
                                  sheet_name = 'variables')

# Interim output library path.
interim_library_path = r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim'

# Set seed.
set_seed = 130816

#------------------------------------------------------------#
# STEP 2: custom modules                                     #
#------------------------------------------------------------#

import data_getter
import dummy
import outlier_treatment
import missings_treatment
import train_test
import first_line_shortlist
import oversampling
import binning_and_transforming
import multicollinearity
import models

#------------------------------------------------------------#
# STEP 3: preprocessing definitions                          #
#------------------------------------------------------------#


def preprocess_1(df0, variable_mapping0, set_seed, target,
                 feature_transformation_metric):
    ''' This preprocessor function can take in WoE and binning feature transfo-
        rmation approaches. '''
    
    start_time = datetime.now()
    
    # Data import and basic wrangles.
    df, variable_mapping = data_getter.ingest_data(df0, variable_mapping0)
    
    # Train-test split.
    df_train, df_test = train_test.split_train_test(df, set_seed, target)    
    
    # Binning and WoE.
    df_train, df_test =\
        binning_and_transforming.bin_and_transform(df_train,
                                                   df_test,
                                                   target,
                                                   variable_mapping,
                                                   feature_transformation_metric)
    
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')
            
    return df_train, df_test


def preprocess_2(df0, variable_mapping0, set_seed, target):
    ''' This preprocessor function treats raw data and does not transform it.
    '''
   
    start_time = datetime.now()
 
    # Data import and basic wrangles.
    df, variable_mapping = data_getter.ingest_data(df0, variable_mapping0)
    
    # Train-test split.
    df_train, df_test = train_test.split_train_test(df, set_seed, target)    
    
    # Univariate feature exclusions.
    df_train, df_test = first_line_shortlist.iv_shortlist(df_train, df_test,
                                                          target)
    
    # Remove nans of shortliested datasets.
    df_train = missings_treatment.remove_nans(df_train)
    df_test = missings_treatment.remove_nans(df_test)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')
                    
    return df_train, df_test


#------------------------------------------------------------#
# STEP 4: model definitions                                  #
#------------------------------------------------------------#


def logit_woe(df_train, df_test, target, metric):
 
    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)

    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    model = models.model_logit(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')
   
    return
     

def logit_dummy(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)
    
    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
    
    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)
    
    # Train and evaluate models.
    model = models.model_logit(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def logit_raw(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test = multicollinearity.remove_multicollinearity(df_train, 
                                                                   df_test, 
                                                                   target)
    
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_logit(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def ann_woe(df_train, df_test, target, set_seed, metric):
 
    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
    
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_ann(X_train, y_train, set_seed)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def ann_dummy(df_train, df_test, target, set_seed, metric):

    start_time = datetime.now()

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)
    
    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
    
    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)
    
    # Train and evaluate models.
    model = models.model_ann(X_train, y_train, set_seed)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def ann_raw(df_train, df_test, target, set_seed, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test = multicollinearity.remove_multicollinearity(df_train, 
                                                                   df_test, 
                                                                   target)
    
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_ann(X_train, y_train, set_seed)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def knn_woe(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    

    
    # Train and evaluate models.
    model = models.model_knn(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def knn_dummy(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)
    
    # Train and evaluate models.
    model = models.model_knn(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def knn_raw(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_knn(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def svm_woe(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_svm(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)
    
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def svm_dummy(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)
    
    # Train and evaluate models.
    model = models.model_svm(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def svm_raw(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)    
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_svm(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def rf_woe(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_rf(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)
    
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def rf_dummy(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Get dummies.
    df_train = pd.get_dummies(df_train)
    df_test = pd.get_dummies(df_test)

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)
        
    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)
    
    # Train and evaluate models.
    model = models.model_rf(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


def rf_raw(df_train, df_test, target, metric):

    start_time = datetime.now()

    # Remove multicollinearity.
    df_train, df_test =\
        multicollinearity.remove_multicollinearity(df_train,
                                                   df_test, 
                                                   target)    
        
    # Select features.
    #X_train, y_train, X_test, y_test =\
    #    models.select_features(df_train, df_test, target, metric)

    # Define matrices.
    y_test, y_train, X_train, X_test =\
        models.define_matrices(df_train, df_test, target)    
    
    # Train and evaluate models.
    model = models.model_rf(X_train, y_train)
    y_train_pred, y_test_pred = models.predict(X_train, y_train, X_test,
                                               y_test, model)
    models.plot_roc(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_cap(y_train, y_train_pred, y_test, y_test_pred)
    models.plot_ks(y_train, y_train_pred, y_test, y_test_pred)

    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()
    print(f'runtime: {runtime}s')

    return


#------------------------------------------------------------#
# STEP 4: model estimations                                  #
#------------------------------------------------------------#



''' WOE-based models '''

df_train, df_test = preprocess_1(df0, variable_mapping0, set_seed, 
                                 'default_event_flg', 'woe')

logit_woe(df_train, df_test, 'default_event_flg', LogisticRegression())

ann_woe(df_train, df_test, 'default_event_flg', set_seed, LogisticRegression())

knn_woe(df_train, df_test, 'default_event_flg', KNeighborsClassifier())

svm_woe(df_train, df_test, 'default_event_flg', SVC()) # convergence issues

rf_woe(df_train, df_test, 'default_event_flg', RandomForestClassifier())



''' Dummy-based models '''

df_train, df_test = preprocess_1(df0, variable_mapping0, set_seed, 
                                 'default_event_flg', 'bins')

logit_dummy(df_train, df_test, 'default_event_flg', LogisticRegression())

ann_dummy(df_train, df_test, 'default_event_flg', set_seed, LogisticRegression())

knn_dummy(df_train, df_test, 'default_event_flg', KNeighborsClassifier())

svm_dummy(df_train, df_test, 'default_event_flg', SVC())

rf_dummy(df_train, df_test, 'default_event_flg', RandomForestClassifier())



''' Raw data-based models '''

df_train, df_test = preprocess_2(df0, variable_mapping0, set_seed, 
                                 'default_event_flg')

logit_raw(df_train, df_test, 'default_event_flg', LogisticRegression())

ann_raw(df_train, df_test, 'default_event_flg', set_seed, LogisticRegression())

knn_raw(df_train, df_test, 'default_event_flg', KNeighborsClassifier())

svm_raw(df_train, df_test, 'default_event_flg', SVC())

rf_raw(df_train, df_test, 'default_event_flg', RandomForestClassifier())



