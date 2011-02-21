import math

class Threshold(object):
    def filter(self, segments):
        pass

def filter(segments, threshold):
    return [(box, image) for (box, image, area) in segments if area > threshold]

class ConstThreshold(Threshold):
    def __init__(self, pixelThreshold):
        self.pixelThreshold = pixelThreshold
    def filter(self, segments):
        return filter(segments, self.pixelThreshold)

class ProportionThreshold(Threshold):
    def __init__(self, thresholdProportion):
        self.thresholdProportion = thresholdProportion
    def filter(self, segments):
        threshold = max(area for (box, image, area) in segments)*self.thresholdProportion
        return filter(segments, threshold)

class AdaptiveThreshold(Threshold):
    def __init__(self, areaThreshold):
        self.areaThreshold = areaThreshold
    def filter(self, segments):
        areas = [area for (box, image, area) in segments]
        average = sum(areas)/len(areas)
        standardDev = math.sqrt(sum((area - average)**2 for area in areas)/len(areas))
        threshold = math.sqrt(standardDev * average * math.sqrt(average/standardDev) * pow(self.areaThreshold, 2))
        return filter(segments, threshold)
