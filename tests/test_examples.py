from .helpers import run_pylps_example


def test_simple_fire():
    actual = run_pylps_example('simple_fire')

    # TODO come up with a way to autogen this
    expected = [
        "['fluent_initiate', 'fire', [], 0]",
        "['action', 'eliminate', (1, 2)]",
        "['fluent_terminate', 'fire', [], 2]"
    ]

    assert actual == expected


def test_simple_fire_args():
    actual = run_pylps_example('simple_fire_args')

    # TODO come up with a way to autogen this
    expected = [
        "['fluent_initiate', 'fire', ['small'], 0]",
        "['action', 'eliminate', (1, 2)]",
        "['fluent_terminate', 'fire', ['small'], 2]"
    ]

    assert actual == expected


def test_recurrent_fire_args():
    # GIVEN
    actual = run_pylps_example('recurrent_fire')

    print(actual)

    assert 4 == 5
