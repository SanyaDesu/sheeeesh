import random as rnd
import os
import sys

from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QMainWindow, QApplication, QWidget
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QMimeData, Qt
from PyQt5.QtGui import QDrag


SUITS = ["clubs", "diamonds", "hearts", "spades"]
VALUES = [value for value in range(1, 14, 1)]

root = os.path.dirname(sys.argv[0])
clubs = root + "/emblems/clubs.png"
diamonds = root + "/emblems/diamonds.png"
hearts = root + "/emblems/hearts.png"
spades = root + "/emblems/spades.png"
images = {"clubs": clubs,
          "diamonds": diamonds,
          "hearts": hearts,
          "spades": spades}

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.row = None
        self.column = None

    def set_position(self, row, column):
        self.row = row
        self.column = column

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
        self.cards.clear()

    def __reversed__(self):
        return iter(self.cards[::-1])


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

    def locked_card(self, i, j):
        return self.pyramid[i + 1][j] and self.pyramid[i + 1][j + 1] is None

    def card_annihilation(self, card1, card2=None):
        if card1.value == 13:
            self.pyramid[card1.row][card1.column] = None
        elif card1.value + card2.value == 13:
            self.pyramid[card1.row][card1.column] = None
            self.pyramid[card2.row][card2.column] = None
        else:
            print("Mismatched cards")
        return None

    def use_top_card(self):
        card = self.second_deck.pop()
        return card

    def decks_reset(self):
        if self.original_deck.is_empty():
            self.original_deck = self.second_deck.__reversed__()
            self.second_deck.annihilate()

    def get_additional_card(self):
        if not self.original_deck.is_empty():
            card = self.original_deck.pop()
            self.second_deck.append(card)

    def win(self):
        return all(all(x is None for x in y) for y in self.pyramid)


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

    def set_card(self, card):
        self.card = card
        if self.card is not None:
            self.value1_lbl.setText(str(self.card.value))
            self.image_lbl.setPixmap(QtGui.QPixmap.fromImage(QtGui.QImage(images.get(self.card.suit))))

    def mouseMoveEvent(self, e) -> None:
        if self.hasMouseTracking() and e.buttons() == Qt.LeftButton:
            mimedata = QMimeData()
            mimedata.setText(str(self.card.value) + "/" + str(self.card.suit))
            drag = QDrag(self)
            drag.setMimeData(mimedata)
            drag.setHotSpot(e.pos())
            drag.exec_(Qt.MoveAction)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.pf = PlayingField()
        self.pf.fill_pyramid()

        self.rowsBOX = QVBoxLayout()
    

        self.centerWidget = QWidget()
        self.centerWidget.setLayout(self.rowsBOX)
        self.setCentralWidget(self.centerWidget)

    def make_pyramid(self):
        for i in range(len(self.pf.pyramid)):
            row = QHBoxLayout()
            self.rowsBOX.addLayout(row)
            for j in range(i+1):
                row.addWidget(CardWidget(self.pf.pyramid[i][j]))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.make_pyramid()
    window.show()
    sys.exit(app.exec_())