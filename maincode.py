import sys
from AppUI.startSplash import Main

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(open("core/ui/style.css", 'r').read())
        main = Main()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
