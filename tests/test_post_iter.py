from post_iter import PostIter
from itertools import zip_longest


def test_from_iterable() -> None:
    assert all(
        x == y
        for x, y in zip_longest(
            PostIter(a for a in "hello"),
            PostIter.from_iterable("hello"),
        )
    )


def test_map() -> None:
    assert all(
        x == y
        for x, y in zip_longest(
            PostIter.from_iterable("hello").map(lambda s: s.upper()),
            "HELLO",
        )
    )


def test_filter() -> None:
    assert all(
        x == y
        for x, y in zip_longest(
            PostIter.from_iterable("hello").filter(lambda s: s != "l"),
            "heo",
        )
    )


def test_chain() -> None:
    assert all(
        x == y
        for x, y in zip_longest(PostIter.from_iterable("hel").chain("lo"), "hello")
    )


def test_sorted() -> None:
    assert all(
        x == y
        for x, y in zip_longest(PostIter.from_iterable("edcba").sorted(), "abcde")
    )
    assert all(
        x == y
        for x, y in zip_longest(
            PostIter.from_iterable("hello").sorted(reverse=True), "ollhe"
        )
    )
    assert all(
        x == y
        for x, y in zip_longest(
            PostIter.from_iterable([1, 2, 3, 4]).sorted(key=lambda i: -i), [4, 3, 2, 1]
        )
    )


def test_reversed() -> None:
    assert all(
        x == y
        for x, y in zip_longest(PostIter.from_iterable("hello").reversed(), "olleh")
    )


def test_next() -> None:
    assert PostIter.empty().next() is None
    assert PostIter.from_iterable("a").next() is "a"


def test_skip() -> None:
    assert PostIter.from_iterable("a").skip().next() is None
    assert all(
        x == y for x, y in zip_longest(PostIter.from_iterable("hello").skip(n=2), "llo")
    )


def test_take() -> None:
    assert all(
        x == y for x, y in zip_longest(PostIter.from_iterable("hello").take(4), "hell")
    )


def test_flatten() -> None:

    p = PostIter.from_iterable(["hel", "lo"])
    # reveal_type(p)
    assert all(x == y for x, y in zip_longest(p.flatten(), "hello"))


def test_inspect() -> None:
    count = 0

    def _inspector(_):
        nonlocal count
        count += 1

    assert all(
        x == y
        for x, y in zip_longest(
            PostIter.from_iterable("hello").inspect(_inspector), "hello"
        )
    )
    assert count == 5


def test_filter_safe() -> None:
    start = [{"hello": 1}, {"hello": 2}, {"world": 3}]
    expected = [{"hello": 1}]
    actual = (
        PostIter.from_iterable(start)
        .filter_safe(lambda d: d["hello"] == 1)
        .into(lambda p: list(p))
    )
    assert expected == actual


def test_map_safe() -> None:
    start = [2, 4, "NaN", 8]
    expected = [1, 2, 4]
    actual = (
        PostIter.from_iterable(start)
        .map_safe(lambda i: i / 2)  # type: ignore
        .into(lambda p: list(p))
    )
    assert expected == actual
