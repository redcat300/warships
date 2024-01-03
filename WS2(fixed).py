import random
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.lives = length

    def dots(self):
        ship_dots = []
        for i in range(self.length):
            x = self.bow.x
            y = self.bow.y

            if self.direction == 0:  #горизонтальное положение
                x += i
            elif self.direction == 1:  #вертикальное положение
                y += i

            ship_dots.append(Dot(x, y))

        return ship_dots

    def shoot_at(self, shot):
        return shot in self.dots()

class Board:
    def __init__(self, size=6):
        self.size = size
        self.board = [['O' for _ in range(size)] for _ in range(size)]
        self.ships = []
        self.ships_visible = False

    def are_ships_left(self):
        return any(ship.lives > 0 for ship in self.ships)

    def distance_check(self, dot1, dot2):
        distance = max(abs(dot1.x - dot2.x), abs(dot1.y - dot2.y))
        return distance >= 2

    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or self.board[dot.y - 1][dot.x - 1] == '■':
                raise ValueError("Нельзя разместить корабль здесь.")
        self.ships.append(ship)
        for dot in ship.dots():
            self.board[dot.y - 1][dot.x - 1] = '■'

    def contour(self, ship, verb=False):
        ship_dots = ship.dots()
        for dot in ship_dots:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    current_dot = Dot(dot.x + i, dot.y + j)
                    if not (self.out(current_dot)) and current_dot not in ship_dots:
                        self.board[current_dot.y - 1][current_dot.x - 1] = '.' if verb else 'O'

    def is_free_space(self, ship):
        ship_dots = ship.dots()
        for dot in ship_dots:
            if self.out(dot) or self.board[dot.y - 1][dot.x - 1] == '■':
                return False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    near_dot = Dot(dot.x + i, dot.y + j)
                    if not self.out(near_dot) and self.board[near_dot.y - 1][near_dot.x - 1] == '■':
                        return False
        return True

    def display(self, hide_ships=False):
        print("    1 2 3 4 5 6")
        print("  --------------")
        for i, row in enumerate(self.board, start=1):
            print(f"{i} |", end=' ')
            for j, cell in enumerate(row, start=1):
                if hide_ships and cell == '■':
                    print('O', end=' ')
                else:
                    print(cell, end=' ')
            print("|")
        print("  --------------")

    def out(self, dot):
        return not (1 <= dot.x <= self.size and 1 <= dot.y <= self.size)

    def shot(self, dot):
        if self.out(dot):
            raise ValueError("За пределами доски.")
        elif self.board[dot.y - 1][dot.x - 1] in ['X', 'T', '.']:  # проверяем на 'X', 'T' и '.'
            raise ValueError("Сюда уже стреляли.")

        for ship in self.ships:
            if dot in ship.dots():
                ship.lives -= 1
                if ship.lives == 0:
                    self.contour(ship, verb=True)
                    print("Корабль потоплен!")
                    self.board[dot.y - 1][dot.x - 1] = 'X'
                else:
                    self.board[dot.y - 1][dot.x - 1] = 'X'
                    print("Попадание!")
                return True
        self.board[dot.y - 1][dot.x - 1] = 'T'
        print("Промах!")
        return False


class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                result = self.enemy_board.shot(target)
                return not result  #True при попадании и False при промахе
            except ValueError as e:
                print(e)


    def display(self):
        print("\nДоска игрока:")
        self.board.display()


class User(Player):
    def ask(self):
        while True:
            try:
                x = int(input("Введите координату x: "))
                y = int(input("Введите координату y: "))
                target = Dot(x, y)
                if self.enemy_board.out(target):
                    raise ValueError("Вне доски.")
                elif self.enemy_board.board[target.y - 1][target.x - 1] in ['X', 'T']:
                    raise ValueError("Сюда уже стреляли.")
                break
            except ValueError as e:
                print(e)
        return target


class AI(Player):
    def ask(self):
        x = random.randint(1, self.board.size)
        y = random.randint(1, self.board.size)
        target = Dot(x, y)
        return target


class Game:

    def __init__(self):
        self.player_board = Board()
        self.ai_board = Board()
        self.player_board.ships_visible = True
        self.player = User(self.player_board, self.ai_board)
        self.ai = AI(self.ai_board, self.player_board)
        self.winner = None

    def random_board(self, board):
        ship_counts = {3: 1, 2: 2, 1: 3}

        for length, count in ship_counts.items():
            for _ in range(count):
                while True:
                    direction = random.randint(0, 1)
                    x = random.randint(1, board.size)
                    y = random.randint(1, board.size)
                    bow = Dot(x, y)
                    new_ship = Ship(length, bow, direction)

                    if board.is_free_space(new_ship):
                        board.add_ship(new_ship)
                        break

    def greet(self):
        print("Добро пожаловать в игру \"Морской бой\"!")
        print("Формат: x y (где x и y - координаты)")

    def loop(self):
        while True:
            # Ход игрока
            self.player.move()

            # Отображаем доски
            print("\nВаша доска:")
            self.player.board.display(hide_ships=False)
            print("\nДоска противника:")
            self.ai.board.display(hide_ships=True)

            # Проверяем остались ли корабли у противника
            if not self.ai.board.are_ships_left():
                self.winner = self.player.__class__.__name__
                print(f"Игра окончена! {self.winner} победил!")
                break

            # Ход ИИ
            self.ai.move()

            # Отображаем доски
            print("\nВаша доска:")
            self.player.board.display(hide_ships=False)
            print("\nДоска противника:")
            self.ai.board.display(hide_ships=True)

            # Проверяем остались ли корабли у игрока
            if not self.player.board.are_ships_left():
                self.winner = self.ai.__class__.__name__
                print(f"Игра окончена! {self.winner} победил!")
                break

        if self.winner:
            print(f"Поздравляем! {self.winner} победил!")

    def start(self):
        self.greet()
        self.random_board(self.player_board)
        self.random_board(self.ai_board)
        print("Доски успешно созданы")
        self.loop()
        print("Игра завершена")

if __name__ == "__main__":
    game = Game()
    game.start()