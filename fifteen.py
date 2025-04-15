import tkinter as tk
import random
import time
import heapq
import tkinter.messagebox

class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.g = 0  # Cost from start node to current node
        self.h = self.heuristic()  # Estimated cost from current node to goal node
        self.f = self.g + self.h  # Total estimated cost

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

    def heuristic(self):
        """Manhattan distance heuristic."""
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] is not None:
                    value = self.board[i][j] - 1
                    target_row = value // 3
                    target_col = value % 3
                    distance += abs(i - target_row) + abs(j - target_col)
        return distance

    def get_neighbors(self):
        """Generates neighboring board states."""
        row, col = self.find_tile(None)
        possible_moves = []
        if row > 0:
            possible_moves.append(("Up", (row - 1, col)))
        if row < 2:
            possible_moves.append(("Down", (row + 1, col)))
        if col > 0:
            possible_moves.append(("Left", (row, col - 1)))
        if col < 2:
            possible_moves.append(("Right", (row, col + 1)))

        neighbors = []
        for move, (new_row, new_col) in possible_moves:
            new_board = [row[:] for row in self.board]  # Create a copy
            new_board[row][col], new_board[new_row][new_col] = new_board[new_row][new_col], new_board[row][col]
            neighbors.append(Node(
                [row[:] for row in new_board], self, move  # Deep copy here
            ))
        return neighbors

    def find_tile(self, tile):
        """Finds the coordinates of a tile on the board."""
        for r, row in enumerate(self.board):
            for c, t in enumerate(row):
                if t == tile:
                    return r, c
        return None, None


def solve_puzzle(initial_board):
    """Solves the 8-puzzle using A* algorithm."""
    initial_node = Node(initial_board)
    goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, None]]

    if initial_node.heuristic() == 0:
        return []  # Already solved

    priority_queue = [initial_node]
    heapq.heapify(priority_queue)  # Convert list to heap
    visited = set()

    while priority_queue:
        current_node = heapq.heappop(priority_queue)

        if current_node.board == goal_board:
            path = []
            while current_node.parent:
                path.append(current_node.move)
                current_node = current_node.parent
            return path[::-1]  # Reverse the path to get the correct order

        visited.add(current_node)

        for neighbor in current_node.get_neighbors():
            neighbor.g = current_node.g + 1
            neighbor.f = neighbor.g + neighbor.heuristic()

            if neighbor not in visited:
                heapq.heappush(priority_queue, neighbor)
            else:  # If neighbour is in priority_queue with lower f_score.
                in_queue = False
                for item in priority_queue:
                    if neighbor == item and item.f > neighbor.f:
                        priority_queue.remove(item)
                        heapq.heapify(priority_queue)
                        heapq.heappush(priority_queue, neighbor)
                        in_queue = True
                        break
                if not in_queue and neighbor in visited and neighbor.f < current_node.f:
                    visited.remove(current_node)
                    heapq.heappush(priority_queue, neighbor)

    return None  # No solution found


class MersenneSlide(tk.Frame):
    def __init__(self, master=None, n=9):
        super().__init__(master)
        self.master = master
        self.n = n
        self.size = int(n**0.5)
        if self.size * self.size != self.n:
            raise ValueError("n должно быть полным квадратом")

        # Initialize board first
        self.board = self.create_solved_board(self.size)
        self.empty_row, self.empty_col = self.find_tile(None) # Find the empty tile
        self.board = self.generate_solvable_board(self.size)


        self.buttons = {}
        self.start_time = 0
        self.moves = 0
        self.timer_running = False
        self.solving = False  # flag, whether the puzzle is solving at the moment

        self.create_widgets()

    def create_widgets(self):
        """Создает элементы интерфейса."""
        self.master.title("Пятнашки Мерсенна")

        self.time_label = tk.Label(self.master, text="Время: 0.00", font=("Arial", 14))
        self.time_label.grid(row=0, column=0, columnspan=self.size)

        self.moves_label = tk.Label(self.master, text="Ходы: 0", font=("Arial", 14))
        self.moves_label.grid(row=0, column=self.size, columnspan=self.size)

        for r in range(self.size):
            for c in range(self.size):
                tile = self.board[r][c]
                if tile is not None:
                    button = tk.Button(
                        self.master,
                        text=str(tile),
                        width=5,
                        height=2,
                        font=("Arial", 20),
                        command=lambda t=tile: self.move_tile(t),
                    )
                    button.grid(row=r + 1, column=c)
                    self.buttons[tile] = button
                else:
                    pass #Empty spot without button

        self.new_game_button = tk.Button(
            self.master, text="Новая игра", font=("Arial", 14), command=self.start_new_game
        )
        self.new_game_button.grid(row=self.size + 1, column=0, columnspan=self.size)

        self.solve_button = tk.Button(
            self.master, text="Решить", font=("Arial", 14), command=self.solve_puzzle_gui
        )
        self.solve_button.grid(row=self.size + 1, column=self.size, columnspan=self.size)

        self.update_board()

    def start_new_game(self):
        """Начинает новую игру."""
        self.board = self.generate_solvable_board(self.size)
        self.moves = 0
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()
        self.update_board()
        self.moves_label.config(text="Ходы: 0")

    def update_board(self):
        """Обновляет состояние игрового поля."""

        # Delete all old buttons
        for tile, button in self.buttons.items():
            button.destroy()
        self.buttons = {}


        for r in range(self.size):
            for c in range(self.size):
                tile = self.board[r][c]
                if tile is not None:
                    button = tk.Button(
                        self.master,
                        text=str(tile),
                        width=5,
                        height=2,
                        font=("Arial", 20),
                        command=lambda t=tile: self.move_tile(t),
                    )
                    button.grid(row=r + 1, column=c)
                    self.buttons[tile] = button
                else:
                  self.empty_row = r
                  self.empty_col = c

    def find_tile(self, tile):
        """Находит координаты плитки на поле."""
        for r, row in enumerate(self.board):
            for c, t in enumerate(row):
                if t == tile:
                    return r, c
        return None, None

    def move_tile(self, tile):
        """Перемещает плитку, если это возможно."""
        r, c = self.find_tile(tile)

        if (abs(r - self.empty_row) == 1 and c == self.empty_col) or (abs(c - self.empty_col) == 1 and r == self.empty_row):
            self.board[r][c], self.board[self.empty_row][self.empty_col] = self.board[self.empty_row][self.empty_col], self.board[r][c]
            self.empty_row, self.empty_col = r, c
            self.moves += 1
            self.moves_label.config(text=f"Ходы: {self.moves}")
            self.update_board()  # Обновляем доску после перемещения
            if self.is_solved():
                self.timer_running = False
                self.show_win_message()

    def generate_solvable_board(self, size, num_moves=100):
        """Генерирует решаемое игровое поле путем выполнения случайных ходов."""
        for _ in range(num_moves):
            # Находим соседние плитки для перемещения
            possible_moves = []
            if self.empty_row > 0:
                possible_moves.append(self.board[self.empty_row - 1][self.empty_col])  # Сверху
            if self.empty_row < size - 1:
                possible_moves.append(self.board[self.empty_row + 1][self.empty_col])  # Снизу
            if self.empty_col > 0:
                possible_moves.append(self.board[self.empty_row][self.empty_col - 1])  # Слева
            if self.empty_col < size - 1:
                possible_moves.append(self.board[self.empty_row][self.empty_col + 1])  # Справа

            # Выбираем случайную плитку для перемещения
            tile_to_move = random.choice(possible_moves)
            self.move_tile_nosound(tile_to_move)

        return self.board

    def move_tile_nosound(self, tile):
        """Перемещает плитку, если это возможно, without update."""
        r, c = self.find_tile(tile)

        if (abs(r - self.empty_row) == 1 and c == self.empty_col) or (abs(c - self.empty_col) == 1 and r == self.empty_row):
            self.board[r][c], self.board[self.empty_row][self.empty_col] = self.board[self.empty_row][self.empty_col], self.board[r][c]
            self.empty_row, self.empty_col = r, c

    def create_solved_board(self, size):
        """Создает решенное игровое поле."""
        tiles = list(range(1, size * size))
        tiles.append(None)
        board = [tiles[i:i + size] for i in range(0, len(tiles), size)]
        return board

    def is_solved(self):
        """Проверяет, решена ли головоломка."""
        expected = list(range(1, self.n))
        expected.append(None)
        actual = []
        for row in self.board:
            actual.extend(row)
        return actual == expected

    def update_timer(self):
        """Обновляет таймер."""
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            self.time_label.config(text=f"Время: {elapsed_time:.2f}")
            self.master.after(10, self.update_timer)  # Обновляем каждые 10 миллисекунд

    def show_win_message(self):
        """Выводит сообщение о победе."""
        elapsed_time = time.time() - self.start_time
        message = f"Поздравляем! Вы решили головоломку за {elapsed_time:.2f} секунд и {self.moves} ходов!"
        tk.messagebox.showinfo("Победа!", message)

    def solve_puzzle_gui(self):
        """Solves the puzzle using A* algorithm."""
        if self.solving:  # Prevent multiple solving processes
            return

        self.solving = True
        # Create a deep copy of the board for the A* algorithm
        initial_board = [row[:] for row in self.board]
        solution = solve_puzzle(initial_board)

        if solution:
            self.apply_solution(solution)
        else:
            tk.messagebox.showinfo("Решение", "Решение не найдено.")
            self.solving = False

    def apply_solution(self, solution):
        """Applies the solution moves to the board."""
        self.master.after(100, self.apply_next_move, solution)  # Delay before the 1st step

    def apply_next_move(self, solution):
        """Applies one move and then schedules next. If there are no moves, unsets flag and exists"""
        if solution:
            move = solution.pop(0)  # Take first move

            # Find coordinates from move (map string to tile name)
            r, c = self.find_tile(None)
            tile = None

            if move == "Up":
                tile = self.board[r - 1][c]
            elif move == "Down":
                tile = self.board[r + 1][c]
            elif move == "Left":
                tile = self.board[r][c - 1]
            elif move == "Right":
                tile = self.board[r][c + 1]

            self.move_tile(tile)  # Perform move in GUI update

            self.master.after(100, self.apply_next_move, solution)  # Schedule next move with delay
        else:
            self.solving = False  # Clear solving flag, once moves completed
            self.update_board()


root = tk.Tk()
game = MersenneSlide(master=root, n=9)  # n must be a perfect square (9, 16, 25, etc.)
game.mainloop()
