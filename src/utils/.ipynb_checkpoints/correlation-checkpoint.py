'''
Hashmap Class for emotions and the determined correlation structure for the entire class

This is a global class of sorts for the entire algorithim that creates continuity with the data structure we want to use for the correlation structure.
Every user and every cluster will have a correlation structure that matches the shape of CorStruct. We will use the CorStruct class to also provide display methods.

However, this will only be stored at the highest level of abstraction as to allow the efficiency of numpy vectorized functions to take precednce over the slower OOJ model
that would be established if we used a CorStruct in each of the User objects


@IMPORTANT: emotions must be passed in format --> [('joy,'omg'), ('omg','omg'')....]

'''
import numpy as np 



class CStruct:
  def __init__(self, _K,  emotions):
    self.vectors = [CorrelationStructure(emotions) for i in range(_K)]
    self.emotions = emotions

  def display(self, **kwargs):
    fig, axes = plt.subplots(nrows=len(self.vectors), sharex=True, figsize=(7 , 14))

    if 'yticklabels' not in kwargs:
      kwargs['yticklabels'] = self.emotions
    
    if 'xticklabels' not in kwargs:
      kwargs['xticklabels'] = self.emotions
    
    for idx, i in enumerate(self.vectors):
      i.displayHeat(axes[idx], **kwargs)

  def __getitem__(self, i):
    return self.vectors[i]
  def __repr__(self):
    return ' '.join([repr(elem) for elem in self.vectors])

  def reset(self):
    for i in self.vectors:
      i.reset()
  def getProb(self):
    for i in self.vectors:
      i.getProb()

  def addStruct(self, other):
    for idx, i in enumerate(self.vectors):
      i.vector = i.vector + other[idx].vector
  
  def divideByInt(self, num):
    for i in self.vectors:
      i.vector = i.vector / num
      
  def AvgL1_Norm(self, other):
    norms = 0
    for idx, i in enumerate(self.vectors):
      norms += i.L1_Norm(other[idx])
    return norms / (idx + 1)
  
  def getScores(self):
    for i in self.vectors:
      i.getScore()
    





class CorrelationStructure:
  def __init__(self, _emotions):
    self.shape = (_emotions.shape[0], _emotions.shape[0])
    self.vector = np.zeros(self.shape)
    self.prob = np.zeros(self.shape)
    self.map = {emotion:i for i, emotion in enumerate(_emotions)}

    self.score = np.zeros(self.shape)
  
  def getN(self):
    return self.vector.sum()

  def __getitem__(self, i):
    return self.vector[self.map[i[0]]][self.map[i[1]]]

  def __setitem__(self, i, newValue):
    self.vector[self.map[i[0]]][self.map[i[1]]] = newValue

  def updateCount(self, i):
    self.vector[self.map[i[0]]][self.map[i[1]]] += 1
  
  def __repr__(self):
    return np.array_repr(self.vector)
 
  def reset(self):
    self.vector = np.zeros(self.shape)

  def getProb(self):
    s = self.vector.sum()
    if s > 0:
      self.prob = self.vector / s

  def __add__(self, other):
    return self.vector + other.vector
  
  def displayHeat(self, ax,  **kwargs):
    return sns.heatmap(self.vector, ax=ax,  **kwargs)
  
  def L1_Norm(self, other):
    return np.sum(abs(self.prob - other.prob))

  def getScore(self):
    for ix,x in enumerate(self.map.keys()):
      px = self.vector[self.map[x]].sum()
      for iy,y in enumerate(self.map.keys()):
        py = self.vector[self.map[y]].sum()
        pxy = px*py
        self.score[self.map[x]][self.map[y]] = 1 if self.vector[self.map[x]][self.map[y]] > pxy else 0


  