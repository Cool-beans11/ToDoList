from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QLabel,
    QWidget,
    QStackedWidget,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QStyle,
    QStyleOption,
    QDialog,
    QLineEdit,
    QScrollArea,
)
from functools import partial
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
import sqlite3
import pandas as pd
from datetime import datetime
from calendar import monthrange

conn = sqlite3.connect("ToDoList\\TaskDb.db")
cur = conn.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            TaskHeader TEXT,
            Description TEXT,
            Completed INTEGER DEFAULT 0  
            ) """
)

monthNames = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

dayNames = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


class dayTasksWidgetList(QWidget):
    def __init__(self, taskList):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        for task in taskList:
            taskItem = taskInDay(task)
            self.layout.addWidget(taskItem)

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class NumberAndStatusWidget(QWidget):
    def __init__(self, dayNumber, status):
        super().__init__()
        self.layout = QHBoxLayout()
        self.curStat = status
        self.setLayout(self.layout)
        self.dayNumberLabel = QLabel(str(dayNumber))
        self.status = QWidget()
        self.status.setFixedSize(16, 16)

        self.status.setObjectName("statusSymbol")
        self.layout.addWidget(self.dayNumberLabel)
        self.layout.addWidget(self.status)
        self.ChangeStatus(self.curStat)

    def ChangeStatus(self, status):
        if status == 1:
            self.status.setStyleSheet(
                """
border-radius: 8px;
background-color: #00FF00
"""
            )
        elif status == 0:
            self.status.setStyleSheet(
                """
border-radius: 8px;
background-color: #FF8800
"""
            )
        else:
            self.status.setStyleSheet(
                """
border-radius: 8px;
background-color: #FFFFFF
"""
            )

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class Day(QWidget):
    def __init__(self, dayNumber, day, status, taskList, year, month):
        super().__init__()
        self.date = datetime.strftime(datetime(year, month, dayNumber), "%B %d, %Y")
        self.setMaximumWidth(220)
        self.setFixedHeight(185)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.topHeader = NumberAndStatusWidget(dayNumber, status)
        self.dayNumber = dayNumber
        self.day = day
        self.dayLabel = QLabel(self.day)
        self.dayTasksWidgetList = dayTasksWidgetList(taskList)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.dayTasksWidgetList)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.layout.addWidget(self.topHeader)
        self.layout.addWidget(self.dayLabel)
        self.layout.addWidget(self.scrollArea)
        self.layout.addStretch()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.today = None
        if datetime.now().date().month + 2 > 12:
            self.MaxForwardMonth = datetime.now().date().month + 2 - 12
        else:
            self.MaxForwardMonth = datetime.now().date().month + 2
        if datetime.now().date().month - 2 < 1:
            self.MaxBackwardMonth = datetime.now().date().month - 2 + 12
        else:
            self.MaxBackwardMonth = datetime.now().date().month - 2
        self.currentMonthNum = datetime.now().date().month
        self.currentYear = datetime.now().date().year
        self.monthsAllowed = range(self.MaxBackwardMonth, self.MaxForwardMonth)
        self.layout = QGridLayout()
        self.layout.setHorizontalSpacing(5)
        self.setLayout(self.layout)
        self.days = monthrange(datetime.now().date().year, datetime.now().date().month)
        self.days = self.days[1]
        self.month = QLabel("")
        arrowLeft = QPixmap("ToDoList\\Resources\\arrow-left-svgrepo-com.svg")
        arrowRight = QPixmap("ToDoList\\Resources\\arrow-right-svgrepo-com.svg")
        self.forwardBtn = QPushButton()
        self.forwardBtn.setIcon(QIcon(arrowRight))
        self.backBtn = QPushButton()
        self.backBtn.setIcon(QIcon(arrowLeft))
        self.month.setObjectName("monthLabel")
        self.layout.addWidget(self.month, 0, 0, 1, 1)
        self.layout.addWidget(self.backBtn, 0, 5, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(
            self.forwardBtn, 0, 6, 1, 1, Qt.AlignmentFlag.AlignHCenter
        )
        self.constructCalendar(self.currentYear, self.currentMonthNum)

    def constructCalendar(
        self,
        year,
        monthNum,
    ):
        count = self.layout.count() - 1
        while count >= 0:
            removeWidget: QWidget = self.layout.itemAt(count).widget()
            if isinstance(removeWidget, QPushButton) or isinstance(
                removeWidget, QLabel
            ):
                count -= 1
                continue
            removeWidget.setParent(None)
            count -= 1
        if monthNum < 1:
            year = year - 1
            monthNum = monthNum + 12
        if monthNum > 12:
            year = year + 1
            monthNum = monthNum - 12
        self.currentMonthNum = monthNum
        self.currentYear = year

        # Disconnect existing connections to avoid multiple executions
        try:
            self.forwardBtn.clicked.disconnect()
            self.backBtn.clicked.disconnect()
        except TypeError:
            pass  # No connections to disconnect

        self.forwardBtn.clicked.connect(
            partial(
                self.constructCalendar,
                self.currentYear,
                self.currentMonthNum + 1,
            )
        )
        self.backBtn.clicked.connect(
            partial(
                self.constructCalendar,
                self.currentYear,
                self.currentMonthNum - 1,
            )
        )
        self.month.setText(f"{monthNames[self.currentMonthNum]} {self.currentYear}")
        i = 1
        rowNum = 1
        columnNum = 0
        noOfDays = monthrange(self.currentYear, self.currentMonthNum)[1]
        while i <= noOfDays:
            status = None
            sqlKey = datetime.strftime(
                datetime(self.currentYear, self.currentMonthNum, i), "%B %d, %Y"
            )
            cur.execute(f"SELECT * FROM Tasks WHERE Date = '{sqlKey}'")
            tasksDoneOnADay = cur.fetchall()
            taskListOnThatDay = []
            for task in tasksDoneOnADay:
                if task[4] == 0:
                    taskListOnThatDay.append((task[2], task[0]))
            if taskListOnThatDay:
                status = 0
            elif not taskListOnThatDay and tasksDoneOnADay:
                status = 1
            if datetime.strftime(
                datetime(self.currentYear, self.currentMonthNum, i), "%B %d, %Y"
            ) == datetime.strftime(datetime.today(), "%B %d, %Y"):
                dayWidget = Day(
                    i,
                    dayNames[
                        datetime(self.currentYear, self.currentMonthNum, i).weekday()
                    ],
                    status,
                    taskListOnThatDay,
                    self.currentYear,
                    self.currentMonthNum,
                )
                self.today = dayWidget
            else:
                dayWidget = Day(
                    i,
                    dayNames[
                        datetime(self.currentYear, self.currentMonthNum, i).weekday()
                    ],
                    status,
                    taskListOnThatDay,
                    self.currentYear,
                    self.currentMonthNum,
                )  # Make the calendar
            self.layout.addWidget(dayWidget, rowNum, columnNum, 1, 1)
            i += 1
            if columnNum == 6:
                rowNum += 1
                columnNum = 0
                continue
            columnNum += 1
        print(self.currentMonthNum, self.MaxForwardMonth, self.MaxBackwardMonth)
        if self.currentMonthNum == self.MaxForwardMonth:
            self.forwardBtn.hide()
            return
        else:
            self.forwardBtn.show()
        if self.currentMonthNum == self.MaxBackwardMonth:
            self.backBtn.hide()
        else:
            self.backBtn.show()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class Dialog(QDialog):
    def __init__(self, msg: str):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # Make the dialog borderless
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.cancelOp = False
        self.proceedOp = False
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.msg = QLabel(msg)
        self.btns = BtnGroup()
        self.layout.addWidget(self.msg)
        self.layout.addWidget(self.btns)
        self.btns.acceptBtn.clicked.connect(self.okAction)
        self.btns.cancelBtn.clicked.connect(self.cancelAction)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor("#928ADF")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def okAction(self):
        self.proceedOp = True
        self.close()

    def cancelAction(self):
        self.cancelOp = True
        self.close()


class BtnGroup(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.acceptBtn = QPushButton("Ok")
        self.cancelBtn = QPushButton("Cancel")
        self.layout.addWidget(self.acceptBtn)
        self.layout.addWidget(self.cancelBtn)


class TaskDialog(QDialog):
    def __init__(self, taskContainerRef, CalendarWidget):
        super().__init__()
        self.taskContainerRef = taskContainerRef
        self.CalendarWidget = CalendarWidget
        self.setWindowFlags(Qt.FramelessWindowHint)  # Make the dialog borderless
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 150)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.taskHeader = QLineEdit()
        self.taskHeader.setPlaceholderText("What is your task?")
        self.description = QLineEdit()
        self.description.setPlaceholderText("Enter a short description for your task")
        self.btns = BtnGroup()
        self.btns.cancelBtn.clicked.connect(self.Cancel)
        self.btns.acceptBtn.clicked.connect(self.addTask)
        self.layout.addStretch(1)
        self.layout.addWidget(self.taskHeader, 3)
        self.layout.addWidget(self.description, 3)
        self.layout.addWidget(self.btns, 3)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor("#928ADF")))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def Cancel(self):
        self.destroy()

    def addTask(self):
        cur.execute("select seq from sqlite_sequence WHERE name='Tasks'")
        LastId = cur.fetchall()
        if self.CalendarWidget.today.dayTasksWidgetList.layout.count() == 0:
            self.CalendarWidget.today.topHeader.ChangeStatus(0)
        if not LastId:
            LastId = 0
        else:
            LastId = LastId[0][0]
        task = Task(
            self.taskHeader.text(),
            self.description.text(),
            0,
            LastId + 1,
            self.CalendarWidget,
        )
        cur.execute(
            f"""INSERT INTO Tasks (Date,TaskHeader,Description) VALUES ('{datetime.strftime(datetime.date(datetime.today()),"%B %d, %Y")}','{self.taskHeader.text()}','{self.description.text()}')"""
        )
        self.CalendarWidget.today.dayTasksWidgetList.layout.addWidget(
            taskInDay((self.taskHeader.text(), LastId + 1))
        )
        conn.commit()
        self.taskContainerRef.addTask(task)
        self.destroy()


class Task(QWidget):
    def __init__(self, Header, description, completed, id, calendar):
        super().__init__()
        self.calendar = calendar
        self.setFixedHeight(50)
        self.taskId = id
        self.completed = False
        if completed == 1:
            self.completed = True
        self.taskHeader = QLabel(str(Header))
        self.taskHeader.setObjectName("taskHeader")
        self.taskHeader.setMinimumHeight(35)
        self.description = QLabel(str(description))
        self.description.setObjectName("description")
        self.description.setMaximumWidth(320)
        tickIcon = QPixmap("ToDoList\\Resources\\tick-svgrepo-com.svg")
        crossIcon = QPixmap("ToDoList\\Resources\\cross-svgrepo-com.svg")
        self.tickMark = QPushButton()
        self.tickMark.setMaximumWidth(40)
        self.tickMark.setIcon(QIcon(tickIcon))
        self.tickMark.clicked.connect(self.CompleteTask)
        self.crossIcon = QPushButton()
        self.crossIcon.setMaximumWidth(40)
        self.crossIcon.setIcon(QIcon(crossIcon))
        self.crossIcon.clicked.connect(self.deleteTask)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setRowMinimumHeight(0, 35)
        self.layout.addWidget(self.taskHeader, 0, 0)
        self.layout.addWidget(self.description, 1, 0)
        self.layout.addWidget(self.tickMark, 0, 3)
        if not self.completed:
            self.layout.addWidget(self.crossIcon, 0, 4)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setHorizontalSpacing(0)

    def deleteTask(self):
        dialog = Dialog("Do you really want to delete this task?")
        dialog.exec()
        if dialog.proceedOp:
            self.setParent(None)
            cur.execute(f"DELETE FROM Tasks WHERE id = {self.taskId}")
            conn.commit()
            return
        if dialog.cancelOp:
            dialog.destroy()
            return

    def CompleteTask(self):
        self.completed = True
        cur.execute(f"UPDATE Tasks SET completed = 1 WHERE id = {self.taskId}")
        conn.commit()
        count = self.calendar.today.dayTasksWidgetList.layout.count()
        while count >= 0:
            try:
                targetWidget = self.calendar.today.dayTasksWidgetList.layout.itemAt(
                    count
                ).widget()
            except:
                count -= 1
                continue
            if targetWidget.taskId == self.taskId:
                targetWidget.setParent(None)
            count -= 1
        count = self.calendar.today.dayTasksWidgetList.layout.count()
        if count == 0:
            self.calendar.today.topHeader.ChangeStatus(1)
        self.crossIcon.hide()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class taskInDay(QWidget):
    def __init__(self, task: tuple):
        super().__init__()
        taskLabel = QLabel(task[0])
        self.taskId = task[1]
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(taskLabel)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class TaskContainer(QWidget):
    def __init__(self, calendar):
        super().__init__()
        self.calendar = calendar
        self.layout = QVBoxLayout()
        self.layout.setSpacing(30)  # Set spacing between task widgets
        self.setLayout(self.layout)
        # QHBoxLayout.setContentsMargins()
        self.layout.addStretch()
        cur.execute(
            f"SELECT * FROM Tasks WHERE Date = '{datetime.strftime(datetime.date(datetime.today()), "%B %d, %Y")}'"
        )
        taskInDb = cur.fetchall()
        for task in taskInDb:
            self.addTask(
                Task(
                    task[2],
                    task[3],
                    task[4],
                    task[0],
                    self.calendar,
                )
            )

    def addTask(self, task: Task):
        self.layout.insertWidget(0, task)

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class TaskBar(QWidget):
    def __init__(self, CalendarWidget):
        super().__init__()
        self.setMinimumWidth(340)
        self.dateLabel = QLabel(
            datetime.strftime(datetime.date(datetime.today()), "%B %d, %Y")
        )
        self.CalendarWidget = CalendarWidget
        self.taskContainer = TaskContainer(self.CalendarWidget)
        self.addTaskBtn = QPushButton()
        plusBtn = QPixmap("ToDoList\\Resources\\plus-large-svgrepo-com.svg")
        self.addTaskBtn.setIcon(QIcon(plusBtn))
        self.addTaskBtn.setMaximumWidth(40)
        self.addTaskBtn.clicked.connect(self.addBtnClick)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dateLabel, 1)
        self.layout.addWidget(self.taskContainer, 7)
        self.layout.addWidget(self.addTaskBtn, 1, Qt.AlignmentFlag.AlignCenter)

    def addBtnClick(self):
        dialog = TaskDialog(self.taskContainer, self.CalendarWidget)
        dialog.exec()

    def paintEvent(self, pe):
        o = QStyleOption()
        o.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, o, p, self)


class MainModule(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.calendar = Calendar()
        self.taskBar = TaskBar(self.calendar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.taskBar, 0, 0, 5, 1)
        self.layout.addWidget(self.calendar, 0, 1, 5, 5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Tracker")
        self.setGeometry(0, 0, 900, 700)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.mainModule = MainModule()
        self.central = QStackedWidget()
        self.setCentralWidget(self.central)
        self.central.addWidget(self.mainModule)
        self.central.setCurrentWidget(self.mainModule)


app = QApplication()
window = MainWindow()
window.show()
with open(
    "ToDoList\\stylesheet.qss",
) as f:
    style = f.read()
    app.setStyleSheet(style)
app.exec()
