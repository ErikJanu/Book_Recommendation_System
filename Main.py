from PyQt5.QtWidgets import QApplication
import sys
from data_processing.Index import Index
from gui.GUI import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(Index().get_indexed_dataset())
    window.show()
    sys.exit(app.exec_())
