from utils import HeadingStopper

def one_test(curr_hdg, dir, target_hdg, hdgs_dont_stop, hdgs_do_stop):
    hs = HeadingStopper(curr_hdg, dir, target_hdg)
    for hdg in hdgs_dont_stop:
        assert not hs.should_stop(hdg), f"Expected {hdg} to not stop"
    for hdg in hdgs_do_stop:
        assert hs.should_stop(hdg), f"Expected {hdg} to stop"

# First test case
one_test(10, 'R', 270, [10, 20, 30, 260, 269], [270, 280, 290, 300])
one_test(270, 'L', 10, [270, 260, 20, 11], [10, 5])
one_test(270, 'R', 90, [270, 265, 280, 360, 0, 1, 89], [90, 91])
one_test(300, 'L', 340, [300, 290, 10, 0, 360, 341], [340, 339])
