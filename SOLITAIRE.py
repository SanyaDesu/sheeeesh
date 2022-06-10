import random as rnd
import os
import sys

from PyQt5.QtWidgets import QPushButton, QMainWindow, QApplication, QMessageBox
from PyQt5 import uic, QtGui

SUITS = ["clubs", "diamonds", "hearts", "spades"]
VALUES = [value for value in range(1, 14, 1)]

root = os.path.dirname(sys.argv[0])
clubs = root + "/emblems/clubs.png"
diamonds = root + "/emblems/diamonds.png"
hearts = root + "/emblems/hearts.png"
spades = root + "/emblems/spades.png"
cardback = root + "/emblems/cardback.png"
circle = root + "/emblems/circle.png"
images = {
    "clubs": clubs,
    "diamonds": diamonds,
    "hearts": hearts,
    "spades": spades,
}


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.row = None
        self.column = None
        self.blocked = False

    def set_position(self, row, column):
        self.row = row
        self.column = column

    def set_blocked_status(self, blocked):
        self.blocked = blocked

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value in VALUES:
            self.__value = value

    @property
    def suit(self):
        return self.__suit

    @suit.setter
    def suit(self, suit):
        if suit in SUITS:
            self.__suit = suit

    @property
    def blocked(self):
        return self.__blocked

    @blocked.setter
    def blocked(self, blocked):
        self.__blocked = blocked

    def __str__(self):
        return f"{self.value} {self.suit}"

    def __repr__(self):
        return f"{self.value} {self.suit}"


class Deck:
    def __init__(self):
        self.cards = []

    def build(self):
        for suit in SUITS:
            for value in VALUES:
                self.cards.append(Card(value, suit))

    def __str__(self):
        return ", ".join(str(c) for c in self.cards)

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = rnd.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def pop(self):
        return self.cards.pop()

    def append(self, card):
        return self.cards.append(card)

    def is_empty(self):
        if not self.cards:
            return True
        return False

    def annihilate(self):
        return self.cards.clear()


class PlayingField:
    def __init__(self):

        self.original_deck = Deck()
        self.original_deck.build()

        self.second_deck = Deck()

        self.pyramid = [[] for i in range(7)]

    def fill_pyramid(self):
        self.original_deck.shuffle()
        for i in range(len(self.pyramid)):
            for j in range(i + 1):
                card = self.original_deck.pop()
                self.pyramid[i].append(card)
                card.set_position(i, j)

    def check_for_blocked_cards(self):
        for i in range(len(self.pyramid)):
            for j in range(i+1):
                if self.pyramid[i][j] is not None:
                    self.pyramid[i][j].set_blocked_status(self.blocked_card(i, j))

    def blocked_card(self, i, j):
        if i < 6:
            return self.pyramid[i + 1][j] or self.pyramid[i + 1][j + 1] is not None

    def card_annihilation(self, comparison):
        if comparison[0].value == 13:
            if comparison[0].row and comparison[0].column is not None:
                self.pyramid[comparison[0].row][comparison[0].column] = None
        elif comparison[0].value + comparison[1].value == 13:
            if comparison[0].row and comparison[0].column is not None:
                self.pyramid[comparison[0].row][comparison[0].column] = None
            if comparison[1].row and comparison[1].column is not None:
                self.pyramid[comparison[1].row][comparison[1].column] = None
        else:
            print("Mismatched cards")


    def use_top_card(self):
        card = self.second_deck.pop()
        return card

    def decks_reset(self):
        if self.original_deck.is_empty():
            while len(self.second_deck.cards) > 0:
                card = self.second_deck.pop()
                self.original_deck.append(card)
            print(pf.original_deck)

    def get_additional_card(self):
        if not self.original_deck.is_empty():
            card = self.original_deck.pop()
            self.second_deck.append(card)

    def win(self):
        return all(all(x is None for x in y) for y in self.pyramid)


comparison = []


class CardWidget(QPushButton):

    def __init__(self, card=None, parent=None):
        super().__init__(parent)

        self.ui = uic.loadUi(root + "/ui/card.ui")
        self.value1_lbl = self.ui.Value1
        self.image_lbl = self.ui.Img

        self.set_card(card)

        self.setLayout(self.ui.layout())
        self.setMinimumSize(self.ui.minimumSize())
        self.setMaximumSize(self.ui.maximumSize())

        self.clicked.connect(self.card_clicked)

    def set_card(self, card):
        self.card = card
        if self.get_blocked_status():
            self.value1_lbl.hide()
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(cardback)))
        elif self.card is not None:
            self.value1_lbl.show()
            self.value1_lbl.setText(str(self.card.value))
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(images.get(self.card.suit))))

    def get_blocked_status(self):
        return self.card.blocked

    def card_clicked(self):
        if not self.card.blocked:
            if len(comparison) == 2:
                pf.card_annihilation(comparison)
                pf.check_for_blocked_cards()
                window.update_pyramid()
                window.repaint()
                comparison.clear()

            elif len(comparison) < 2:
                comparison.append(self.card)


class Slot(QPushButton):
    def __init__(self, string, parent=None):
        super().__init__(parent)

        self.string = string

        self.ui = uic.loadUi(root + "/ui/card.ui")
        self.value1_lbl = self.ui.Value1
        self.image_lbl = self.ui.Img

        self.set_slot()

        self.setLayout(self.ui.layout())
        self.setMinimumSize(self.ui.minimumSize())
        self.setMaximumSize(self.ui.maximumSize())

        self.setFlat(True)

    def set_slot(self):
        self.value1_lbl.setText(self.string)
        self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage()))


class OriginalDeckWidget(QPushButton):
    def __init__(self, deck=None, parent=None):
        super().__init__(parent)

        self.ui = uic.loadUi(root + "/ui/card.ui")
        self.value1_lbl = self.ui.Value1
        self.image_lbl = self.ui.Img

        self.value1_lbl.hide()
        self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(cardback)))

        self.clicked.connect(self.deck_clicked)

        self.set_deck(deck)

        self.setLayout(self.ui.layout())
        self.setMinimumSize(self.ui.minimumSize())
        self.setMaximumSize(self.ui.maximumSize())

    def set_deck(self, deck):
        self.deck = deck

    def deck_clicked(self):
        if not self.deck.is_empty():
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(cardback)))
            pf.get_additional_card()
            window.second_deck.set_card()
            print(pf.second_deck)
        else:
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(circle)))
            pf.decks_reset()


class SecondDeckWidget(QPushButton):
    def __init__(self, deck=None, parent=None):
        super().__init__(parent)

        self.ui = uic.loadUi(root + "/ui/card.ui")
        self.value1_lbl = self.ui.Value1
        self.image_lbl = self.ui.Img

        self.value1_lbl.hide()
        self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(circle)))

        self.set_deck(deck)

        self.set_card()

        self.clicked.connect(self.deck_clicked)

        self.setLayout(self.ui.layout())
        self.setMinimumSize(self.ui.minimumSize())
        self.setMaximumSize(self.ui.maximumSize())

    def set_deck(self, deck):
        self.deck = deck

    def set_card(self):
        if len(self.deck.cards) > 0:
            self.card = self.deck.cards[-1]
            if self.card is not None:
                self.value1_lbl.show()
                self.value1_lbl.setText(str(self.card.value))
                self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(images.get(self.card.suit))))

    def deck_clicked(self):
        if not self.deck.is_empty():
            card = self.deck.pop()
            comparison.append(card)
            self.set_card()
        else:
            self.value1_lbl.hide()
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(circle)))



class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.win_msg = QMessageBox()
        self.win_msg.setWindowTitle("IMPORTANT")
        self.win_msg.setText("You win!!!!!")

        self.ui = uic.loadUi(root + "/ui/mainwindow.ui")

        self.first = self.ui.first
        self.second = self.ui.second
        self.third = self.ui.third
        self.fourth = self.ui.fourth
        self.fifth = self.ui.fifth
        self.sixth = self.ui.sixth
        self.seventh = self.ui.seventh

        self.decks_layout = self.ui.decks_layout

        self.second_deck = SecondDeckWidget(pf.second_deck)
        self.decks_layout.addWidget(self.second_deck)
        self.decks_layout.addWidget(OriginalDeckWidget(pf.original_deck))

        self.setCentralWidget(self.ui.centralwidget)

        self.setMinimumSize(self.ui.minimumSize())

        self.all_rows = [self.first, self.second, self.third, self.fourth, self.fifth, self.sixth, self.seventh]

    def win_check(self):
        if pf.win():
            self.win_msg.exec_()

    def build_pyramid(self):
            self.first.addWidget(CardWidget(pf.pyramid[0][0]))
            for j in range(2):
                if pf.pyramid[1][j] is not None:
                    self.second.addWidget(CardWidget(pf.pyramid[1][j]))
                else:
                    self.second.addWidget(Slot(""))
            for j in range(3):
                if pf.pyramid[2][j] is not None:
                    self.third.addWidget(CardWidget(pf.pyramid[2][j]))
                else:
                    self.third.addWidget(Slot(""))
            for j in range(4):
                if pf.pyramid[3][j] is not None:
                    self.fourth.addWidget(CardWidget(pf.pyramid[3][j]))
                else:
                    self.fourth.addWidget(Slot(""))
            for j in range(5):
                if pf.pyramid[4][j] is not None:
                    self.fifth.addWidget(CardWidget(pf.pyramid[4][j]))
                else:
                    self.fifth.addWidget(Slot(""))
            for j in range(6):
                if pf.pyramid[5][j] is not None:
                    self.sixth.addWidget(CardWidget(pf.pyramid[5][j]))
                else:
                    self.sixth.addWidget(Slot(""))
            for j in range(7):
                if pf.pyramid[6][j] is not None:
                    self.seventh.addWidget(CardWidget(pf.pyramid[6][j]))
                else:
                    self.seventh.addWidget(Slot(""))

    def update_pyramid(self):
        for i in self.all_rows:
            for j in reversed(range(i.count())):
                i.itemAt(j).widget().setParent(None)
        self.build_pyramid()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pf = PlayingField()
    pf.fill_pyramid()
    pf.check_for_blocked_cards()
    window = MainWindow()
    window.build_pyramid()
    window.show()
    sys.exit(app.exec_())
