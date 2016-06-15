from simlord.simlord import calculate_cigar_operations

MATCH, DELETION, INSERTION, SUBST = (7, 2, 1, 8)  # PySam CIGAR Operation Codes


def test_all_matches():
    result = calculate_cigar_operations(100, [], [], [])
    assert result == [(MATCH, 100)]


def test_all_inserts():
    result = calculate_cigar_operations(100, list(range(100)), [], [])
    assert result == [(INSERTION, 100)]


def test_all_deletion():
    # 100 deletions in a row result in 100 new bases that match if the other lists are empty
    result = calculate_cigar_operations(100, [], [0]*100, [])
    assert result == [(DELETION, 100), (MATCH, 100)]


def test_all_substitution():
    result = calculate_cigar_operations(100, [], [], list(range(100)))
    assert result == [(SUBST, 100)]


def test_every_second_deletion():
    result = calculate_cigar_operations(10, [], list(range(10)), [])
    assert result == [(DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1),(DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1)]


def test_1():
    result = calculate_cigar_operations(10, [0,1,2,3], [4,5,6], [6])
    assert result == [(INSERTION, 4), (DELETION, 1), (MATCH, 1), (DELETION, 1), (MATCH, 1), (DELETION, 1), (SUBST, 1), (MATCH, 3)]



def test_2():
    result = calculate_cigar_operations(10, [1,2], [2,2,5,5], [])
    assert result == [(MATCH, 1), (INSERTION, 1), (DELETION, 2), (INSERTION, 1), (MATCH, 2), (DELETION, 2), (MATCH, 5)]