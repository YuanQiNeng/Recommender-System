import numpy as np
import pandas as pd
from typing import Union
from tqdm import tqdm
class LSH:
    def __init__(self,L:int=100,K:int=100):
        self.L=L #number of iterations
        self.K=K #Number of randomly generated lines
    def fit(self,X:np.ndarray):
        if not isinstance(X,np.ndarray):
            raise TypeError('X should np.ndarray')
        neighbors=[set() for _ in range(X.shape[0])]
        for i in tqdm(range(self.L)):
            W=np.random.uniform(low=-10,high=10,size=(X.shape[-1],self.K))
            trans=np.where(X@W>0,1,0)
            negihbor=self.get_neighbor(trans)
            for j,y in enumerate(negihbor):
                neighbors[j]=neighbors[j].union(y)
        return neighbors #Return the nearest neighbors of each vector
    def get_neighbor(self,trans:np.ndarray):
        #Get the neighbors of each 0-1 vector
        res=[]
        label_sum=np.sum(trans,axis=1)
        for i in range(trans.shape[0]):
            muti_sum_ndarray=(trans[i]*trans).sum(axis=1)
            indexs=np.where(muti_sum_ndarray==label_sum[i])[0]
            res.append(indexs.tolist()[1:])
        return res