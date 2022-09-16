
import numpy as np
from src.utils.scenes import Scenes
from src.utils.correlation import CStruct




class Cluster:
  def __init__(self,_K, _emotions,_df, _users, _cluster):
    self.users = _users
    self.clusterId = _cluster
    self.sceneInfo = Scenes(_df, _users)
    self.struct = CStruct(_K, _emotions)
  
  def updateCentroid(self, userData):
    self.struct.reset()
    for ithUser in self.users:
      self.struct.addStruct(userData[ithUser].struct)
    self.struct.getProb()

  def updateCentroid2(self, otherCluster, globalUsers):
    otherK = otherCluster.clusterId
    self.struct[otherK].reset()
    for i in self.users:
      _u = globalUsers[i]
      for sidx, scene in enumerate(_u.scenes):
        _u_response = _u.emotions[sidx]
        oresponses = otherCluster.sceneInfo[scene][1]
        for osid, os in enumerate(oresponses):
          self.struct[otherK].updateCount((_u_response, os))
    self.struct[otherK].getProb()

  def setUsers(self, users):
    self.users = users
    self.sceneInfo.updateUsers(self.users)

  def displaySceneInfo(self, userData, **kwargs):
    sceneData = []
    for ithU in self.users:
      __u = userData[ithU]
      sceneData.append(__u.emotions)
    value, counts = np.unique(np.hstack(sceneData), return_counts=True)
    sns.barplot(x=value, y=counts, **kwargs)

    
