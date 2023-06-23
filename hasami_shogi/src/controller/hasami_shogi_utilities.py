def bi_dict(dictionary):
    """Given a dictionary, adds all values as keys and their keys as values. Does not work if values are mutable."""
    temp_dict = dict(dictionary)
    for key, value in temp_dict.items():
        dictionary[value] = key


# CONSTANTS
row_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
col_labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

row_num = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8}
col_num = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8}
all_squares_in_order = [row + col for row in row_num for col in col_num]
bi_dict(row_num)
bi_dict(col_num)
all_squares = set(all_squares_in_order)
CORNER_CAP_PIECES = {
    'a2': 'b1',
    'b1': 'a2',
    'a8': 'b9',
    'b9': 'a8',
    'h1': 'i2',
    'i2': 'h1',
    'h9': 'i8',
    'i8': 'h9'
}


def run_moves(game, move_list):
    """Takes game object and list of 4-string moves."""
    return [game.make_move(move[:2], move[2:]) for move in move_list]


def index_to_string(row, column):
    """Converts row/column index (indexed at 0) to square string. Assumes valid input."""
    return row_num[row] + col_num[column]


def string_to_index(square_string):
    """Returns the indices of the given square string as a tuple. O(1)"""
    return row_num[square_string[0]], col_num[square_string[1]]


def opposite_color(color):
    """Returns RED if BLACK, and vice versa."""
    return {"RED": "BLACK", "BLACK": "RED"}[color]


def get_game_pieces(game):
    """Given a game, returns a {'color': {square string set}} dictionary. Does not contain empty squares."""
    output = {"RED": set(), "BLACK": set()}
    for square in all_squares_in_order:
        square_occupant = game.get_square_occupant(square)
        if square_occupant in output:
            output[square_occupant].add(square)
    return output

def get_all_pieces(game_piece_dict):
    """Returns set of all pieces on gameboard without any reference to color."""
    return game_piece_dict["RED"] | game_piece_dict["BLACK"]

def get_piece_color(game_piece_dict, piece):
    """Given a game piece dict, returns the color of the given piece, or None if not found. Assumes legit piece."""
    if piece in game_piece_dict["RED"]:
        return "RED"
    if piece in game_piece_dict["BLACK"]:
        return "BLACK"
    return None


def get_adjacent_squares(square_string):
    """Returns all directly adjacent pieces of the given square string."""
    row, col = string_to_index(square_string)
    poss_rows = row+1, row-1
    poss_cols = col+1, col-1
    return {index_to_string(x, col) for x in poss_rows if 0<=x<9} | {index_to_string(row, y) for y in poss_cols if 0<=y<9}


def get_next_square(square_string1, square_string2):
    """Given two adjacent square strings, gives the next square in a line. Returns None if off board. Assumes valid input."""
    if not square_string1 or not square_string2:
        return None
    (row1, col1), (row2, col2) = string_to_index(square_string1), string_to_index(square_string2)
    row_dir, col_dir = row2 - row1, col2 - col1
    next_row, next_col = row2 + row_dir, col2 + col_dir
    if 0 <= next_row < 9 and 0 <= next_col < 9:
        return index_to_string(next_row, next_col)
    return None


def build_square_string_range(square_string_from, square_string_to):
    """Returns list of square strings from first square to second. Range cannot be diagonal. Assumes valid input."""
    if not square_string_from or not square_string_to:
        return None

    if square_string_from[0] != square_string_to[0] and square_string_from[1] != square_string_to[1]:
        return None

    # 1. Convert square strings to indices.
    row_from, col_from = string_to_index(square_string_from)
    row_to, col_to = string_to_index(square_string_to)

    # 2. Generate ranges. There should be exactly one range of length 0.
    row_min, row_max = min(row_to, row_from), max(row_to, row_from)
    col_min, col_max = min(col_to, col_from), max(col_to, col_from)
    row_range, col_range = range(row_min, row_max + 1), range(col_min, col_max + 1)

    # 3. Generate list of square strings from ranges. Reverse output if necessary.
    output_range = [index_to_string(row, col) for row in row_range for col in col_range]
    return output_range if row_from <= row_to and col_from <= col_to else output_range[::-1]


def return_valid_moves(game, square_string):
    """Returns all valid moves for the given square. O(1)"""
    if game.get_square_occupant(square_string) == game.get_active_player():
        valid_moves = set()

        # Get coords of all adjacent squares
        adj_squares = get_adjacent_squares(square_string)

        # Check all adjacent squares for vacancy. If vacant, check next in path. If not, check next direction.
        for square in adj_squares:
            curr_square = square
            next_square = get_next_square(square_string, square)
            while curr_square:
                if game.get_square_occupant(curr_square) != "NONE":
                    break
                else:
                    valid_moves.add(square_string+curr_square)
                    curr_square, next_square = next_square, get_next_square(curr_square, next_square)

        return valid_moves
    else:
        raise Exception("Given square string is not active player.")