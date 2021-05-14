class ScenePriority:
  def __init__(self, df, content, min):
    c = df[df.contentIdx == content]

    self.title = c.iloc[1,:]['title']
    self.df = c.groupby(['sceneIdx', 'emotion']).size().groupby(level=0).apply( lambda x:  100*x / x.sum()).unstack().reset_index(drop=True).fillna(0)
    self.df.columns.name = None
    self.summary = self.df.describe()
    self.variances = self.standardizedSceneVariances()
    #makes it easier to get scenes
    self.scenes = self.getTopScenes(min)
  def displayScenes(self):
    nScenes = self.df.shape[0]
    return self.df.plot(kind='bar', stacked=True, figsize=(30,3), title=f"""Distribution of Emotions (%) By Scene ({self.title})""")

  def displayVariances(self):
    ax = sns.heatmap(pd.DataFrame(map, index=self.df.columns).transpose(), cmap=sns.diverging_palette(145, 300, s=60, as_cmap=True))
    ax.set(ylabel='Scene')
    return ax
  def standardizedSceneVariances(self):
    map = []
    for idx, scene in self.df.iterrows():
      avg = []
      for ithEmotion in np.array(scene.index):
        currentVal = scene[ithEmotion]
        mean = self.summary.loc['mean', ithEmotion]
        std = self.summary.loc['std', ithEmotion]

        standardized = (currentVal - mean) / std
        avg.append(standardized)
      map.append( avg)
    return map

  def getMaxVariances(self):
    maxVariance = []
    for idx, varianceAr in enumerate(self.variances):

      maxVariance.append([idx,np.amax(abs(np.array(varianceAr)))])

    return sorted(maxVariance, key=lambda x: x[1], reverse=True)
  
  def getTopScenes(self, minScenes=1):
    # total scenes in content
    totalScenes = self.df.shape[0]

    # if there are no enough scenes, just return as many as possible
    if minScenes > totalScenes:
      minScenes = totalScenes
        
    ar = self.getMaxVariances()

    indices = [] 

    for i in range(0, minScenes):
      indices.append(ar[i][0])

    return indices
  

  def displayTop(self, top, title):
    positions = [i for i in range(0, len(top))]

    f, (avg, all) = plt.subplots(1, 2)

    width = 1
    c =sns.color_palette("husl", 9)

    bottomPadding = np.zeros(len(positions))

    for idx, emotion in enumerate(self.df.columns):
      row =[]
      for sceneId in top:
        row.append(self.df.loc[sceneId, emotion])
      all.bar(positions, 
              row ,width=width, 
              bottom = bottomPadding , 
              color=c[idx])
      bottomPadding = np.add(bottomPadding, row)

    all.set_xticks(positions, minor=False)
    all.set_xticklabels(top, minor=False)
    all.set_yticks([])
    all.set_xlabel("Scene Index")

    bottomPadding = 0
    for idx,i in enumerate(self.summary.loc['mean']):
      avg.bar(0, i, bottom=bottomPadding, color= c[idx] )
      bottomPadding += i
    avg.set_xticks([0])
    avg.set_xlabel("Average Scene")
    avg.legend(self.df.columns, loc='upper left', prop={'size':7})
    avg.set_xmargin(2)
    plt.subplots_adjust(wspace=.10)
    plt.title(title)

  def scenesGreaterThanThreshold(self, threshold=0.25):
    scenes = []
    for idx, row in self.df.iterrows():
      if max(row) > threshold * 100:
        scenes.append(idx)
    return scenes
      
   