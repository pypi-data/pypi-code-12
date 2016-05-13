"""
.. module sgsclient.example.tictactoe.simple

An example client for TicTacToe that plays in the next available space.

When executed directly it will call :func:`sgsclient.main` with
``supported_games = ["tictactoe"]``.
"""

from sgsclient import StratumGSClientInstance, main

class TicTacToeClient(StratumGSClientInstance):
    """
        An example TicTacToe client that plays in the next available space.
    """

    def __init__(self, *args):
        super(TicTacToeClient, self).__init__(*args)
        self._board = None
        self._winner = None

    def server_closed_connection(self):
        """
            Print out the end status of the game when the server closes the
            connection.
        """

        print("Game Over!")
        if self._winner:
            print("Player {} wins!".format(self._winner))
        else:
            print("Draw!")

    def _find_empty_cell(self):
        """
            Find the next empty square in the board.

            :returns: A tuple of the row and column of the empty square.
        """

        for r, row in enumerate(self._board):
            for c, cell in enumerate(row):
                if cell is None:
                    return r, c

    def message_received_from_server(self, message):
        """
            Handle a received message from the server.
        """

        if message["type"] == "state":
            self._board = message["board"]
            self._winner = message["winner"]
        elif message["type"] == "turn":
            row, col = self._find_empty_cell()
            self.send_message_to_server({
                "type": "move",
                "row": row,
                "column": col
            })


if __name__ == "__main__":
    main(TicTacToeClient, supported_games=["tictactoe"])
