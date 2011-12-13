def test_evens():
    for i in range(0, 5):
        yield check_even, i*2
        yield check_even, i*2

def check_even(n):
    assert n % 2 == 0