"""
.. module sgsclient.example.tictactoe.manual

An example client for TicTacToe that prompts the user for input.

When executed directly it will call :func:`sgsclient.main` with
``supported_games = ["tictactoe"]`` and ``max_games = 1``.
"""

import functools
from sgsclient import StratumGSClientInstance, main


class TicTacToeClient(StratumGSClientInstance):
    """
        An example TicTacToe client that prompts the user for input.
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

    def _make_move(self):
        """
            Makes a move. Prompts the user for input until they provide a valid
            move, then sends that move to the server.
        """

        while True:
            move = input("Your Move? (row, column) ")
            try:
                row, col = (int(x.strip()) for x in move.split(","))
            except:
                print("Invalid input value.")
                continue
            break
        self.send_message_to_server({
            "type": "move",
            "row": row,
            "column": col
        })

    
    def message_received_from_server(self, message):
        """
            Handle a received message from the server.
        """

        if message["type"] == "state":
            self._board = message["board"]
            self._winner = message["winner"]
        elif message["type"] == "turn":
            print("\nYour turn!")
            board = list(map(lambda x: x or " ", functools.reduce(lambda x, y: x+y, self._board, [])))
            print("\n{} | {} | {}\n---------\n{} | {} | {}\n---------\n{} | {} | {}\n".format(*board))
            self._make_move()
        elif message["type"] == "repeat-turn":
            print("The server rejected your last move.")
            print("The error was:", message["error"])
            self._make_move()



if __name__ == "__main__":
    main(TicTacToeClient, supported_games=["tictactoe"], max_games=1)
