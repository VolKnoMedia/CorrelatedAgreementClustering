import numpy as np


class SceneHeuristic:
    def __init__(self, results):
        self.results = np.array(results)
        self.emotions = np.unique(self.results[:, 2])
        self.emotionDict = {i:idx for idx,i in enumerate(self.emotions)}

    def getProb(self):
        scenes = self.results[:, 1].astype(int)
        nScenes = np.unique(scenes)
        counts = [[0 for k in self.emotions] for i in range(nScenes.shape[0])]
        # get counts
        for i in self.results:
            scene = int(i[1])
            emotion = i[2]
            counts[scene][self.emotionDict[emotion]] += 1

        # calculate probabilities
        for ii, scenIdx in enumerate(counts):
            _sum = sum(scenIdx)
            for xx, emot in enumerate(scenIdx):
                emot = emot/_sum
                counts[ii][xx] = emot
        return np.array(counts)
        
    def getStandardVariances(self):
        probs = self.getProb()
        variance = []
        for sceneIdx, i in enumerate(probs):
            sceneVariance = []
            for ithEmotion, value in self.emotionDict.items():
                currentVal = probs[sceneIdx][value]

                mean = probs[:,value].mean()
                std =  probs[:,value].std()

                standard = (currentVal - mean ) / std
                sceneVariance.append(standard)
            variance.append(sceneVariance)
        return variance
    
    def getMaxVariances(self):
        maxVariance = []
        variances = self.getStandardVariances()
        for idx, variance in enumerate(variances):
            maxVariance.append([idx, max(abs(ele) for ele in variance)])
        return sorted(maxVariance, key=lambda x: x[1], reverse=True)

    def getTopScenes(self, nScenes=1):
        if nScenes < 1:
            raise Exception("Scene Must be more than 1")
        scenes = self.results[:, 1].astype(int)
        totalScenes = np.unique(scenes).shape[0]
        if nScenes > totalScenes:
            nScenes = totalScenes

        sortedVariances = np.array(self.getMaxVariances())

        return sortedVariances[:nScenes, 0]

        

    