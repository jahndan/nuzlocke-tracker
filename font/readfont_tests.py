from readfont import match_color, check_content, crop_content
import numpy

palette = [
    [0, 255, 0, 0],
    [1, 0, 0, 1],
    [0, 2, 0, 2],
    [3, 0, 3, 0],
    [4, 0, 0, 4],
    [5, 0, 0, 5],
    [6, 6, 0, 0],
    [0, 0, 0, 0],
]


def match_color_test():
    tests = []
    for color in palette:
        tests.append(match_color(numpy.array(color), numpy.array([0, 255, 0, 0])))
    answers = [True, False, False, False, False, False, False, False]
    print("===match_color() tests===")
    for i in range(len(tests)):
        print(f"Test {i}")
        if tests[i] == answers[i]:
            print("OK")
        else:
            print("FAIL")
    # TODO test edge cases like non-colors being passed in


def check_content_test():
    print("===check_content() tests===")
    tests = [
        numpy.array([palette[i] for i in [0, 1, 2, 3, 4, 5, 6, 7]]),
        numpy.array([palette[i] for i in [1, 1, 1, 1, 1, 1, 1, 1]]),
        numpy.array([palette[i] for i in [0, 0, 0, 0, 7, 7, 7, 7]]),
        numpy.array([palette[i] for i in [7, 0, 7, 0, 7, 0]]),
        numpy.array([palette[i] for i in [0, 7, 0, 0]]),
        numpy.array([palette[i] for i in [0, 0, 0, 1]]),
        numpy.array([palette[i] for i in [0, 0, 0, 0, 0, 0, 0, 0]]),
        numpy.array([palette[i] for i in [0, 0, 0, 0]]),
        numpy.array([palette[i] for i in [0, 0]]),
        numpy.array([palette[i] for i in [0]]),
    ]
    answers = [True, True, True, True, True, True, False, False, False, False]
    for i in range(len(tests)):
        print(f"Test {i}")
        if check_content(tests[i]) == answers[i]:
            print("OK")
        else:
            print("FAIL")
    # TODO test edge cases like wrongly-sized inputs and debug info provided


def crop_content_one():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_two():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 0, 0, 0],
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
            [0, 0, 0, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_three():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 0, 1, 2, 3, 0],
            [0, 3, 0, 1, 2, 0],
            [0, 2, 3, 0, 1, 0],
            [0, 1, 2, 3, 0, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_four():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 3, 0],
            [0, 3, 0, 1, 2, 0],
            [0, 2, 3, 0, 1, 0],
            [0, 1, 2, 3, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 2, 3],
            [3, 0, 1, 2],
            [2, 3, 0, 1],
            [1, 2, 3, 0],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_five():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 7, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 0, 6, 0, 3, 0],
            [0, 0, 5, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [2, 0, 0, 7, 0],
            [0, 0, 0, 1, 0],
            [0, 4, 0, 0, 0],
            [0, 0, 6, 0, 3],
            [5, 0, 0, 0, 0],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_six():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 1, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
    ]
    answer = [
        [palette[i] for i in lst]
        for lst in [
            [1],
        ]
    ]
    return numpy.array(test), numpy.array(answer)


def crop_content_seven():
    test = [
        [palette[i] for i in lst]
        for lst in [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
    ]
    return numpy.array(test), None


def crop_content_test():
    print("===crop_content() tests===")
    print("Test 1")
    test, answer = crop_content_one()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 2")
    test, answer = crop_content_two()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 3")
    test, answer = crop_content_three()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 4")
    test, answer = crop_content_four()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 5")
    test, answer = crop_content_five()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 6")
    test, answer = crop_content_six()
    attempt = crop_content(test)
    if numpy.array_equal(attempt, answer):
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)

    print("Test 7")
    test, answer = crop_content_seven()
    attempt = crop_content(test)
    if attempt == answer:
        print("OK")
    else:
        print("FAIL")
        print("expected:")
        print(answer)
        print("received:")
        print(attempt)


match_color_test()
check_content_test()
crop_content_test()
