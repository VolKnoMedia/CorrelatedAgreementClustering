'''
Lookup table for users. And implementation with bracket notation
Input:  df = dataframe with userId's, scenehash, and then the corresponding emotion
        users: if set to 'all', all users in df will be indexed, pass in <array> of usersId's otherwise

'''

import pandas as pd
import numpy as np


class Users:
  def __init__(self, df, users):
    self.data = df.loc[df.user.isin(users), df.columns.intersection(['user','hash','emotion'])].to_numpy()
    users = df.user.unique() if users == 'all' else users
    self.lookup = {ithUser:np.where(self.data == ithUser) for ithUser in users}

  def getData(self, user):
    # use as mask
    idx = self.lookup[user][0]
    return self.data[idx].transpose(1,0)[1:]
  
  def __getitem__(self, attr):
    return self.getData(attr)
