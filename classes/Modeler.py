# -*- coding: utf-8 -*-
"""
"""

#------------------------------------------------------------#
# STEP 1: setup                                              #
#------------------------------------------------------------#

from dataclasses import dataclass 

import pandas as pd
import numpy as np

from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
#from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import roc_curve, auc
#from sklearn.metrics import precision_recall_curve, PrecisionRecallDisplay
import matplotlib.pyplot as plt

#------------------------------------------------------------#
# STEP 2: definitions                                        #
#------------------------------------------------------------#


@dataclass(frozen = False)
class Modeler:
    
    df_train: pd.DataFrame
    df_test: pd.DataFrame
    target: str
    selection_metric: object
    set_seed: int
    
    def select_features(self):
            
        # Define algorithms
        sfs = SequentialFeatureSelector(self.selection_metric,
                                        n_features_to_select = 15,
                                        direction = 'forward',
                                        cv = 5)

        # Define X and y.
        self.y_test = self.df_test.loc[:, self.target]
        self.y_train = self.df_train.loc[:, self.target]
        self.X_train = self.df_train.loc[:, self.df_train.columns != self.target]
        
        # Fit.
        sfs.fit(self.X_train, self.y_train)

        # Update X matrices with sfs.
        self.X_train = sfs.transform(self.X_train)
        self.X_test = self.df_test[list(sfs.get_feature_names_out())]
        
        print(list(sfs.get_feature_names_out()))
        
        return (self.X_train, self.y_train, self.X_test, self.y_test)
    
    
    def model_logit(self):
        
        self.logit = LogisticRegression(solver = 'saga', max_iter = 1000,
                                   penalty = None)
        self.logit.fit(self.X_train, self.y_train)

        SM = sm.Logit(self.y_train, self.X_train).fit()
        print(SM.summary())

        return self.logit
    
    
    def model_ann(self):
        
        mlp = MLPClassifier(max_iter = 1000, random_state = self.set_seed,
                            early_stopping = True)
        
        hyperparameter_grid = {
            'hidden_layer_sizes': [(7),
                                   (5, 5),
                                   (7, 7),
                                   (10, 5),
                                   (10, 10),
                                   (20, 20),
                                   (40, 40, 20),
                                   (40, 20, 20),
                                   (20, 40, 20),
                                   (100, 200, 100),
                                   (200, 100, 100),
                                   (200, 200, 100),
                                   (200, 400, 200)],
            'activation': ['logistic', 'tanh', 'relu'],
            'solver': ['adam'],
            'learning_rate': ['constant', 'invscaling', 'adaptive'],
        }
        
        self.ann = GridSearchCV(mlp, hyperparameter_grid, n_jobs = -1, cv = 5)
        
        self.ann.fit(self.X_train, self.y_train)
        
        print('Best parameters found:\n', self.ann.best_params_)
        
        for mean, std, params in zip(self.ann.cv_results_['mean_test_score'],
                                     self.ann.cv_results_['std_test_score'],
                                     self.ann.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))    
            
        return self.ann
    
 
    def model_knn(self):

        k_range = list(range(1, 10))
        hyperparameter_grid = {
            'n_neighbors' : k_range,
            'weights' : ('uniform', 'distance'),
            'leaf_size' : [(10), (30), (50), (70), (90), (150)],
            'p' : [(1), (2)]
            }
        
        self.knn = GridSearchCV(KNeighborsClassifier(), hyperparameter_grid, 
                                n_jobs = -1, cv = 5)
        
        self.knn.fit(self.X_train, self.y_train)

        print('Best parameters found:\n', self.knn.best_params_)
        
        for mean, std, params in zip(self.knn.cv_results_['mean_test_score'],
                                     self.knn.cv_results_['std_test_score'],
                                     self.knn.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))
        
        return self.knn


    def model_svm(self):
    
        svc = SVC(max_iter = 1000, probability = True, cache_size = 5000)
    
        hyperparameter_grid = {
            'C' : [(0), (0.1), (0.2), (0.3), (0.4), (0.5),
                   (0.6), (0.7), (0.8), (0.9), (1)],
            'kernel' : ('linear', 'poly', 'rbf', 'sigmoid'),
            'degree' : [(1), (2), (3), (4), (5)]
            }
        
        self.svm = GridSearchCV(svc, hyperparameter_grid, n_jobs = -1, cv = 5)
        
        self.svm.fit(self.X_train, self.y_train)
     
        print('Best parameters found:\n', self.svm.best_params_)
        
        for mean, std, params in zip(self.svm.clf.cv_results_['mean_test_score'],
                                     self.svm.clf.cv_results_['std_test_score'],
                                     self.svm.clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))   
     
        return self.svm


    def model_rf(self):
    
        self.rf = RandomForestClassifier(max_depth = 2, random_state = 0)
        self.rf.fit(self.X_train, self.y_train)
      
        return self.rf


    def run(self):
        
        self.select_features()
        self.model_logit()
        self.model_ann()
        self.model_knn()
        self.model_svm()
        self.rf()
        
        return (self.logit, self.ann, self.knn, self.svm, self.rf)
    
    
    
    
    