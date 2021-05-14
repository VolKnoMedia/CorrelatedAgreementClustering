import numpy as np
import pandas as pd




class Scenes:
  def __init__(self, df, users):
    self.globalDf = df.loc[:, df.columns.intersection(['user','hash','emotion'])]
    self.data = self.globalDf.loc[self.globalDf.user.isin(users), :].to_numpy()
    hash = np.unique(self.data.transpose()[2]) 
    self.lookup = {ith:np.where(self.data == ith) for ith in hash}

  def getData(self, hash):
    # use as mask
    try:
      idx = self.lookup[hash][0]
      return self.data[idx].transpose(1,0)[:2]
    except:
      return np.array([ np.array([]),np.array([]) ])

  def updateUsers(self, users):
    self.data = self.globalDf.loc[self.globalDf.user.isin(users), :].to_numpy()
    hash = np.unique(self.data.transpose()[2]) 
    self.lookup = {ith:np.where(self.data == ith) for ith in hash}

  
  def __getitem__(self, attr):
    return self.getData(attr)