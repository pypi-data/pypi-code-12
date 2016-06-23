def dashed_line(length: int, symbol: str="=") -> str:
    """Print out a dashed line

        To be used as visual boundaries for tests.

        Args:
            length (int): number of charters
            symbol (str): symbol to be used in the dashed line
                default: "="

        Returns:
            a string of characters of length `n`.
    """
    def aux(length, accum):
        if length == 0:
            return accum
        else:
            return aux(length - 1, accum + symbol)
    return aux(length, "")
