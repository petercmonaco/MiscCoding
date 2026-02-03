import nav_learning

def expect_y(learner, x, expected_y):
    pred_y = learner.predict(x)
    assert abs(pred_y - expected_y) <= 0.001, f"At x={x}, expected y={expected_y}, got {pred_y}"

# Start with two points on the line y = x
l1 = nav_learning.RegressionLearner(-7, -7, 4, 4, 5)
expect_y(l1, 0.5, 0.5)
expect_y(l1, 2, 2)
# Now give it 5 new points on the line y = 0.5x + 3
# these should push the original points out of the window
for i in range(5):
    l1.add_point(i, 0.5*i + 3)
expect_y(l1, 0, 3)
expect_y(l1, 2, 4)
expect_y(l1, 6, 6)

