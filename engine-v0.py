import chess
import chess.polyglot


class Engine:
    def __init__(self, color_to_play, render=False, search_depth=3, alpha=-100000, beta=100000, custom_fen=None):
        self.color = color_to_play
        self.depth = search_depth
        self.alpha = alpha
        self.beta = beta
        self.render = render
        if custom_fen:
            self.board = chess.Board(fen=custom_fen)
        else:
            self.board = chess.Board()

        self.pawn_table = [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, -20, -20, 10, 10, 5,
            5, -5, -10, 0, 0, -10, -5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, 5, 10, 25, 25, 10, 5, 5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
            0, 0, 0, 0, 0, 0, 0, 0]

        self.knight_table = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50]

        self.bishop_table = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -20, -10, -10, -10, -10, -10, -10, -20]

        self.rook_table = [
            0, 0, 0, 5, 5, 0, 0, 0,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            5, 10, 10, 10, 10, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0]

        self.queen_table = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 5, 5, 5, 5, 5, 0, -10,
            0, 0, 5, 5, 5, 5, 0, -5,
            -5, 0, 5, 5, 5, 5, 0, -5,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20]

        self.king_table = [
            20, 30, 10, 0, 0, 10, 30, 20,
            20, 20, 0, 0, 0, 0, 20, 20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30]

    def _evaluate_board(self):
        if self.board.is_checkmate():
            if self.board.turn:
                return -9999
            else:
                return 9999

        if self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0

        # Count all the black & white pieces
        white_pawn = len(self.board.pieces(chess.PAWN, chess.WHITE))
        black_pawn = len(self.board.pieces(chess.PAWN, chess.BLACK))
        white_rook = len(self.board.pieces(chess.ROOK, chess.WHITE))
        black_rook = len(self.board.pieces(chess.ROOK, chess.BLACK))
        white_bishop = len(self.board.pieces(chess.BISHOP, chess.WHITE))
        black_bishop = len(self.board.pieces(chess.BISHOP, chess.BLACK))
        white_knight = len(self.board.pieces(chess.KNIGHT, chess.WHITE))
        black_knight = len(self.board.pieces(chess.KNIGHT, chess.BLACK))
        white_queen = len(self.board.pieces(chess.QUEEN, chess.WHITE))
        black_queen = len(self.board.pieces(chess.QUEEN, chess.BLACK))

        material_score = (100 * (white_pawn - black_pawn)) + (320 * (white_knight - black_knight)) + \
                         (330 * (white_bishop - black_bishop)) + (500 * (white_rook - black_rook)) + \
                         (900 * (white_queen - black_queen))

        king_score = sum([self.king_table[pos] for pos in self.board.pieces(chess.KING, chess.WHITE)]) - \
                     sum([self.king_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.KING,
                                                                                                 chess.BLACK)])
        pawn_score = sum([self.pawn_table[pos] for pos in self.board.pieces(chess.PAWN, chess.WHITE)]) - \
                     sum([self.pawn_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.PAWN,
                                                                                                 chess.BLACK)])
        rook_score = sum([self.rook_table[pos] for pos in self.board.pieces(chess.ROOK, chess.WHITE)]) - \
                     sum([self.rook_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.ROOK,
                                                                                                 chess.BLACK)])
        bishop_score = sum([self.bishop_table[pos] for pos in self.board.pieces(chess.BISHOP, chess.WHITE)]) - \
                       sum([self.bishop_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.BISHOP,
                                                                                                     chess.BLACK)])
        knight_score = sum([self.knight_table[pos] for pos in self.board.pieces(chess.KNIGHT, chess.WHITE)]) - \
                       sum([self.knight_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.KNIGHT,
                                                                                                     chess.BLACK)])
        queen_score = sum([self.queen_table[pos] for pos in self.board.pieces(chess.QUEEN, chess.WHITE)]) - \
                      sum([self.queen_table[chess.square_mirror(pos)] for pos in self.board.pieces(chess.QUEEN,
                                                                                                   chess.BLACK)])

        evaluated_score = material_score + king_score + queen_score + rook_score + bishop_score + knight_score + \
                          pawn_score

        if self.board.turn:
            return evaluated_score
        else:
            return -evaluated_score

    def _quiescence_search(self, alpha, beta):
        static_eval = self._evaluate_board()
        if static_eval >= beta:
            return beta
        if alpha < static_eval:
            alpha = static_eval

        for move in self.board.legal_moves:
            if self.board.is_capture(move):
                self.board.push(move)
                score = -self._quiescence_search(-beta, -alpha)
                self.board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        return alpha

    def _alpha_beta_pruning(self, alpha, beta, depth_left):
        best_score = -9999
        if depth_left == 0:
            return self._quiescence_search(alpha, beta)

        for move in self.board.legal_moves:
            self.board.push(move)
            score = -self._alpha_beta_pruning(-beta, -alpha, depth_left - 1)
            self.board.pop()
            if score >= beta:
                return score
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score

        return best_score

    def _select_move(self, depth):
        # Try a book opening
        try:
            book_move = chess.polyglot.MemoryMappedReader('bookfish.bin').weighted_choice(self.board).move
            return book_move

        except:
            print("Thinking.....")
            best_move = chess.Move.null()
            best_value = -99999
            alpha = self.alpha
            beta = self.beta
            for move in self.board.legal_moves:
                self.board.push(move)
                board_value = -self._alpha_beta_pruning(-beta, -alpha, depth - 1)
                self.board.pop()
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
                if board_value > alpha:
                    alpha = board_value

            return best_move

    def play(self):

        while not self.board.is_game_over():
            if self.board.turn == self.color:
                move = self._select_move(self.depth)
                self.board.push(move)
                print("My Move : ", move)
                print(self.board)
            else:
                opponent_move = input("Enter your move : ")
                try:
                    self.board.push_san(opponent_move)
                except:
                    print("Not a valid san input/ Move is illegal. Enter a new move")

        print("Good Game !")


if __name__ == '__main__':
    # Change color here
    engine = Engine(chess.WHITE)
    engine.play()
