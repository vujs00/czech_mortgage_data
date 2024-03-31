# -*- coding: utf-8 -*-
"""
@author: Stevan Vujcic

"""

#------------------------------------------------------------#
# STEP 1: setup                                              #
#------------------------------------------------------------#

import pandas as pd
#import numpy as np
from sklearn.linear_model import LogisticRegression
from mlxtend.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
#from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import roc_curve, auc
#from sklearn.metrics import precision_recall_curve, PrecisionRecallDisplay
import matplotlib.pyplot as plt

df_train = pd.read_parquet(r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\06_-_df_train.parquet')
df_smot_train = pd.read_parquet(r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\06_-_df_smot_train.parquet')

df_test = pd.read_parquet(r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\06_-_df_test.parquet')
df_smot_test = pd.read_parquet(r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\06_-_df_smot_test.parquet')

sfs_vars_export_path = r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\07-2_-_sfs_selected_features.xlsx'
sfs_smot_vars_export_path = r'C:\Users\JF13832\Downloads\Thesis\03 Data\02 Interim\07-2_-_sfs_smot_selected_features.xlsx'

#------------------------------------------------------------#
# STEP 2: define function                                    #
#------------------------------------------------------------#

def neural_network(df_train,
                   df_test,
                   sfs_vars_export_path,
                   model_output_name):
    
    ''' Model estimation '''
    
    # Define algorithms
    sfs = SequentialFeatureSelector(LogisticRegression(),
                                    k_features = 10,
                                    forward = True, # Options are forward and backward
                                    scoring = 'roc_auc', # Options are 'accuracy', 'roc_auc'
                                    cv = 5) 

    # Define X and y.
    y_train = df_train.loc[:, 'default_event_flg']
    X_train = df_train.loc[:, df_train.columns != 'default_event_flg']

    # Fit.
    sfs.fit(X_train, y_train)

    # Use chosen features.
    sfs_vars = pd.DataFrame(sfs.k_feature_names_)
    sfs_vars.rename(columns = {0 : 'variable_name'}, inplace = True)
    sfs_vars.to_excel(sfs_vars_export_path)
    sfs_vars = sfs_vars['variable_name'].values.tolist()

    # Re-run the selection of X and y matrices for safety.
    X_train = df_train[sfs_vars]
    y_train = df_train[['default_event_flg']]

    # Fit neural network    
    mlp_gs = MLPClassifier(max_iter = 1000, random_state = 130816,
                           early_stopping = True)
    
    parameter_space = {
        'hidden_layer_sizes': [(7),
                               (10, 5),
                               (7, 7),
                               (5, 5)],
        'activation': ['logistic', 'tanh', 'relu'],
        'solver': ['adam'],
        'learning_rate': ['constant', 'invscaling', 'adaptive'],
    }
    
    clf = GridSearchCV(mlp_gs, parameter_space, n_jobs = -1, cv = 3)
    
    clf.fit(X_train, y_train)
    
    print('Best parameters found:\n', clf.best_params_)
    
    for mean, std, params in zip(clf.cv_results_['mean_test_score'],
                                 clf.cv_results_['std_test_score'],
                                 clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))    
    
    ''' Forecasts '''    
    
    # Train set
    y_train_array = y_train['default_event_flg'].values
    y_train_pred = clf.predict_proba(X_train)[:,1]

    # Test set
    X_test = df_test[sfs_vars]
    y_test = df_test[['default_event_flg']]
    y_test_array = y_test['default_event_flg'].values
    y_test_pred = clf.predict_proba(X_test)[:,1]

    ''' ROC AUC plots '''    
    
    # Plot roc auc
    plt.figure(figsize=(7, 5))
     
    fpr_train, tpr_train, _ = roc_curve(y_train, y_train_pred)
    roc_auc_train = auc(fpr_train, tpr_train)
    
    fpr_test, tpr_test, _ = roc_curve(y_test_array, y_test_pred)
    roc_auc_test = auc(fpr_test, tpr_test)
      
    plt.plot(fpr_train, tpr_train, ':',
             label = f'(train set, AUC = {roc_auc_train:.2f})', color = 'k')
    plt.plot(fpr_test, tpr_test,
             label = f'(test set, AUC = {roc_auc_test:.2f})', color = 'k')
    plt.plot([0, 1], [0, 1], 'r--', color = 'k')
     
    # Labels
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    for pos in ['right', 'top']: 
        plt.gca().spines[pos].set_visible(False) 
    plt.legend()
    plt.legend()
    plt.show()    

#------------------------------------------------------------#
# STEP 4: non-smot-expanded dataset                          #
#------------------------------------------------------------#

neural_network(df_train = df_train, df_test = df_test, 
               sfs_vars_export_path = sfs_vars_export_path, 
               model_output_name = 'ann_summary')

#------------------------------------------------------------#
# STEP 5: smot-expanded dataset                              #
#------------------------------------------------------------#
    
neural_network(df_train = df_smot_train, df_test = df_smot_test, 
               sfs_vars_export_path = sfs_smot_vars_export_path, 
               model_output_name = 'ann_smot_summary')

#------------------------------------------------------------#
# Tryout: brute force neural network                         #
#------------------------------------------------------------#

def neural_network(df_train,
                   df_test):
    
    ''' Model estimation '''
    
    X_train = df_train.loc[:, df_train.columns != 'default_event_flg']
    y_train = df_train[['default_event_flg']]

    # Fit neural network    
    mlp_gs = MLPClassifier(max_iter = 1000, random_state = 130816,
                           early_stopping = True)
    
    parameter_space = {
        'hidden_layer_sizes': [(22),
                               (30, 15),
                               (22, 22),
                               (15, 15)],
        'activation': ['logistic', 'tanh', 'relu'],
        'solver': ['adam'],
        'learning_rate': ['constant', 'invscaling', 'adaptive'],
    }
    
    clf = GridSearchCV(mlp_gs, parameter_space, n_jobs = -1, cv = 3)
    
    clf.fit(X_train, y_train)
    
    print('Best parameters found:\n', clf.best_params_)
    
    for mean, std, params in zip(clf.cv_results_['mean_test_score'],
                                 clf.cv_results_['std_test_score'],
                                 clf.cv_results_['params']):
        print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))    
    
    ''' Forecasts '''    
    
    # Train set
    y_train_array = y_train['default_event_flg'].values
    y_train_pred = clf.predict_proba(X_train)[:,1]

    # Test set
    X_test = df_test.loc[:, df_test.columns != 'default_event_flg']
    y_test = df_test[['default_event_flg']]
    y_test_array = y_test['default_event_flg'].values
    y_test_pred = clf.predict_proba(X_test)[:,1]

    ''' ROC AUC plots '''    
    
    # Plot roc auc
    plt.figure(figsize=(7, 5))
     
    fpr_train, tpr_train, _ = roc_curve(y_train, y_train_pred)
    roc_auc_train = auc(fpr_train, tpr_train)
    
    fpr_test, tpr_test, _ = roc_curve(y_test_array, y_test_pred)
    roc_auc_test = auc(fpr_test, tpr_test)
      
    plt.plot(fpr_train, tpr_train, ':',
             label = f'(train set, AUC = {roc_auc_train:.2f})', color = 'k')
    plt.plot(fpr_test, tpr_test,
             label = f'(test set, AUC = {roc_auc_test:.2f})', color = 'k')
    plt.plot([0, 1], [0, 1], 'r--', color = 'k')
     
    # Labels
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    for pos in ['right', 'top']: 
        plt.gca().spines[pos].set_visible(False) 
    plt.legend()
    plt.legend()
    plt.show()





