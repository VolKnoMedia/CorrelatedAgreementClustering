
import math
import numpy as np
from src.utils.correlation import CStruct


class User:
  def __init__(self, _K , _emotions,_userData, _userId,  _cluster = -1 ):
    self.cluster = [_cluster]
    self.emotions, self.scenes = _userData
    self.id = _userId
    self.struct = CStruct(_K, _emotions)
    self.score = 0
    self.scores = []
    t = np.unique(self.emotions, return_counts=True)
    self.entropy = sum([(i / sum(t[1])) * math.log2((i / sum(t[1]))) for i in t[1]]) * -1

  def setCluster(self, _clusterId):
    self.cluster.append(_clusterId)
  
  def getCluster(self):
    return self.cluster[-1]

  def updateStruct(self, _k, uEmotion, otherEmotions):
    for oEmotion in otherEmotions:
      self.struct[_k].updateCount((uEmotion, oEmotion))
  
  def display(self):
    self.struct.getProb()
    values, counts = np.unique(self.emotions, return_counts=True)
    sns.barplot(x=values, y=counts, ax=f8_ax1).set_title(f""" User {self.id} in cluster {self.getCluster()} (Score : {self.score})""")


  def __repr__(self):
    return "<User id:%s cluster:%s>" % (self.id, self.cluster)
