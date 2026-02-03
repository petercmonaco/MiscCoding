
class RegressionLearner:
    def __init__(self, x1, y1, x2, y2, max_points):
        self.points = [(x1, y1), (x2, y2)]
        self.sum_x = x1 + x2
        self.sum_y = y1 + y2
        self.sum_xx = x1*x1 + x2*x2
        self.sum_xy = x1*y1 + x2*y2
        self.max_points = max_points

    def add_point(self, x, y):
        self.points.append((x, y))
        self.sum_x += x
        self.sum_y += y
        self.sum_xx += x*x
        self.sum_xy += x*y
        while len(self.points) > self.max_points:
            (old_x, old_y) = self.points.pop(0)
            self.sum_x -= old_x
            self.sum_y -= old_y
            self.sum_xx -= old_x*old_x
            self.sum_xy -= old_x*old_y

    def _get_regression(self):
        n = len(self.points)
        denom = n*self.sum_xx - self.sum_x*self.sum_x
        if denom == 0:
            return (0, 0)
        m = (n*self.sum_xy - self.sum_x*self.sum_y) / denom
        b = (self.sum_y - m*self.sum_x) / n
        return (m, b)
    
    def predict(self, x):
        (m, b) = self._get_regression()
        return m*x + b