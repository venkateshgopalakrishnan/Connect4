from typing import Union


class ConnectFour:
    def __init__(self, player: int, game_column: int, board: list[list[int]]):
        self._player = player
        self._game_column: int = game_column
        self._position: Union[int, None] = None
        self._board = board

    @property
    def board(self) -> list[list[int]]:
        if self._board:
            return self._board
        else:
            print('board not set')

    @board.setter
    def board(self, board: list[list[int]]):
        self._board = board

    def check_column_valid(self) -> bool:
        return not bool(self._board[self._game_column][-1])

    def make_move(self) -> (list[list[int]], int):
        new_board: list[list[int]] = self._board
        for position, cell in enumerate(new_board[self._game_column]):
            if not cell:
                new_board[self._game_column][position] = self._player
                self._position = position
                break
        self._board = new_board
        return self._board, self._position

    def check_game_over(self) -> bool:
        return all([bool(col[-1]) for col in self._board])

    def check_win(self) -> list[tuple]:
        row: int = self._game_column
        col: int = self._position
        row_min = col_min = 0
        row_max: int = len(self._board) - 1
        col_max: int = len(self._board[0]) - 1
        target: int = 4 * self._player
        board = self._board

        start_row, stop_row = max(row - 3, row_min), min(row + 3, row_max)
        while start_row + 3 <= stop_row:
            if board[start_row][col] + board[start_row + 1][col] + board[start_row + 2][col] + board[start_row + 3][
                col] == target:
                return [(start_row, col), (start_row + 1, col), (start_row + 2, col), (start_row + 3, col)]
            start_row += 1

        start_col, stop_col = max(col - 3, col_min), min(col + 3, col_max)
        while start_col + 3 <= stop_col:
            if board[row][start_col] + board[row][start_col + 1] + board[row][start_col + 2] + board[row][
                start_col + 3] == target:
                return [(row, start_col), (row, start_col + 1), (row, start_col + 2), (row, start_col + 3)]
            start_col += 1

        start_row, stop_row = max(row - col, row - 3, row_min), min(row + (col_max - col), row + 3, row_max)
        start_col, stop_col = max(col - row, col - 3, col_min), min(col + (row_max - row), col + 3, col_max)
        while start_row + 3 <= stop_row and start_col + 3 <= stop_col:
            if board[start_row][start_col] + board[start_row + 1][start_col + 1] + \
                    board[start_row + 2][start_col + 2] + board[start_row + 3][start_col + 3] == target:
                return [(start_row, start_col), (start_row + 1, start_col + 1), (start_row + 2, start_col + 2),
                        (start_row + 3, start_col + 3)]
            start_row += 1
            start_col += 1

        start_row, stop_row = max(row - (col_max - col), row - 3, row_min), min(row + col, row + 3, row_max)
        start_col, stop_col = max(col - (row_max - row), col - 3, col_min), min(col + row, col + 3, col_max)
        while start_row + 3 <= stop_row and stop_col - 3 >= start_col:
            if board[start_row][stop_col] + board[start_row + 1][stop_col - 1] + \
                    board[start_row + 2][stop_col - 2] + board[start_row + 3][stop_col - 3] == target:
                return [(start_row, stop_col), (start_row + 1, stop_col - 1), (start_row + 2, stop_col - 2),
                        (start_row + 3, stop_col - 3)]
            start_row += 1
            stop_col -= 1
        return []
