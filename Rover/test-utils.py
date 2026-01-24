from nav_utils import HeadingStopper

def one_test(curr_hdg, dir, target_hdg, hdgs_dont_stop, hdgs_do_stop):
    hs = HeadingStopper(curr_hdg, dir, target_hdg)
    for hdg in hdgs_dont_stop:
        assert not hs.should_stop(None, None, hdg), f"Expected {hdg} to not stop"
    for hdg in hdgs_do_stop:
        assert hs.should_stop(None, None, hdg), f"Expected {hdg} to stop"

# Test cases
one_test(10, 'right', 270, [10, 20, 30, 260, 269], [270, 280, 290, 300])
one_test(270, 'left', 10, [270, 260, 20, 11], [10, 5])
one_test(270, 'right', 90, [270, 265, 280, 360, 0, 1, 89], [90, 91])
one_test(300, 'left', 340, [300, 290, 10, 0, 360, 341], [340, 339])
one_test(300, None, 340, [300, 310, 339], [340, 341])
one_test(10, None, 270, [10, 0, 350, 271], [270, 269, 240])
one_test(90, None, 100, [90, 95, 99], [100, 101, 110])
one_test(100, None, 90, [100, 95, 91], [90, 89, 80])