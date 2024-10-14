from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStackedWidget, QTableWidgetItem, QTableWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
import sys
import json

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)

        self.loginPage = LoginUI(self)
        self.mainPage = MainPageUI(self)
        self.testingPage = TestingPageUI(self)
        self.calibrationPage = CalibrationPageUI(self)
        self.reportsPage = ReportsPageUI(self)

        self.stackedWidget.addWidget(self.loginPage)
        self.stackedWidget.addWidget(self.mainPage)
        self.stackedWidget.addWidget(self.testingPage)
        self.stackedWidget.addWidget(self.calibrationPage)
        self.stackedWidget.addWidget(self.reportsPage)
        
        self.stackedWidget.setCurrentWidget(self.loginPage)

        self.showMaximized()

        self.stackedWidget.currentChanged.connect(self.on_page_changed)

    def on_page_changed(self, index):
        current_page = self.stackedWidget.currentWidget()

        if isinstance(current_page, LoginUI):
            self.showMaximized()  
        else:
            self.showFullScreen() 

class LoginUI(QMainWindow):
    def __init__(self, mainUI):
        super(LoginUI, self).__init__()

        loadUi("newLogin.ui",self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('loginCover.jpg');"  
                           "background-position: center;"
                           "}")

        self.loginButton.clicked.connect(self.check_credentials)
        self.mainUI = mainUI

        self.correct_email = "a"
        self.correct_password = "a"

        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('xymaLogoBlue.png')  

        resized_pixmap = pixmap.scaled(200, 100, aspectRatioMode=1) 
    
        self.loginPageXymaLogoLabel.setPixmap(resized_pixmap)
        self.loginPageXymaLogoLabel.setScaledContents(True)

    def check_credentials(self):
        email = self.emailInput.text() 
        password = self.passwordInput.text()  

        if email == self.correct_email and password == self.correct_password:
            self.emailInput.clear()
            self.passwordInput.clear()
            self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage) 
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid email or password. Please try again.")

class MainPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(MainPageUI, self).__init__()
        loadUi("mainPage.ui", self) 

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.logoutButton.clicked.connect(self.logout)
        self.testingButton.clicked.connect(self.GoToTestingPage)
        self.calibrationButton.clicked.connect(self.GoToCalibrationPage)
        self.reportsButton.clicked.connect(self.GoToReportsPage)

        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('xymaLogoWhite.png')  

        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.mainpageXymaLogoLabel.setPixmap(resized_pixmap)
        self.mainpageXymaLogoLabel.setScaledContents(True)

    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)

    def GoToTestingPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.testingPage)

    def GoToCalibrationPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.calibrationPage)

    def GoToReportsPage(self):
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.reportsPage)

class TestingPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(TestingPageUI, self).__init__()
        loadUi("testingPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.testingBackButton.clicked.connect(self.testingGoBack)
        self.testingLogoutButton.clicked.connect(self.logout)

        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('xymaLogoWhite.png')  
        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.XymaLogoLabel.setPixmap(resized_pixmap)
        self.XymaLogoLabel.setScaledContents(True)

    def testingGoBack(self):
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)

    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)

# calibration page
class CalibrationPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(CalibrationPageUI, self).__init__()
        loadUi("calibrationPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI

        self.calibrationBackButton.clicked.connect(self.calibrationGoBack)
        self.calibrationAddButton.clicked.connect(self.addToTable)
        self.calibrationEditButton.clicked.connect(self.enableTableEditing)
        self.calibrationSubmitButton.clicked.connect(self.saveCalibrationData)
        self.logoutButton.clicked.connect(self.logout)

        self.inputsLocked = False
        self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)

        self.load_logo()
        self.populate_table_header()

    def load_logo(self):
        pixmap = QPixmap('xymaLogoWhite.png')  

        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.xymaLogoLabel.setPixmap(resized_pixmap)
        self.xymaLogoLabel.setScaledContents(True)

    def populate_table_header(self):
        headers = ["Fluid Name", "Trial No", "Temperature", "Density", "Viscosity"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)

    def addToTable(self):
        fluidName = self.fluidNameInput.text()
        trialNo = self.trialNoInput.value()
        temperature = self.temperatureInput.value()
        density = self.densityInput.value()
        viscosity = self.viscosityInput.value()

        if not fluidName or not trialNo or temperature is None or density is None or viscosity is None:
            self.show_alert("Please fill in all fields before adding.")
            return

        rowPosition = self.calibrationTable.rowCount()
        self.calibrationTable.insertRow(rowPosition)

        self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(fluidName))
        self.calibrationTable.setItem(rowPosition, 1, QTableWidgetItem(str(trialNo)))
        self.calibrationTable.setItem(rowPosition, 2, QTableWidgetItem(str(temperature)))
        self.calibrationTable.setItem(rowPosition, 3, QTableWidgetItem(str(density)))
        self.calibrationTable.setItem(rowPosition, 4, QTableWidgetItem(str(viscosity)))

        if not self.inputsLocked:
            self.fluidNameInput.setDisabled(True)
            self.trialNoInput.setDisabled(True)
            self.inputsLocked = True

        self.temperatureInput.clear()
        self.densityInput.clear()
        self.viscosityInput.clear()

    def saveCalibrationData(self): 

        if self.calibrationTable.rowCount() == 0:
            self.show_alert('Please add calibration data before submitting')
            return
        
        calibrationJsonFile = 'calibrationData.json'

        try:
            with open(calibrationJsonFile, 'r') as file:
                calibrationFileData = json.load(file)
        except FileNotFoundError: 
            calibrationFileData = {}

        for row in range(self.calibrationTable.rowCount()):
            fluidName = self.calibrationTable.item(row, 0).text()
            trialNo = f"Trial{self.calibrationTable.item(row, 1).text()}"

            temperature = self.calibrationTable.item(row, 2).text()
            density = self.calibrationTable.item(row, 3).text()
            viscosity = self.calibrationTable.item(row, 4).text()

            reading_data = {"Temperature": float(temperature), "Density": float(density), "Viscosity": float(viscosity)}

            if fluidName not in calibrationFileData:
                calibrationFileData[fluidName] = {}

            if trialNo not in calibrationFileData[fluidName]:
                calibrationFileData[fluidName][trialNo] = {}

            readingNo = 1
            while f'reading{readingNo}' in calibrationFileData[fluidName][trialNo]:
                readingNo += 1  

            calibrationFileData[fluidName][trialNo][f'reading{readingNo}'] = [reading_data]  
        
        with open(calibrationJsonFile, 'w') as file:
            json.dump(calibrationFileData, file, indent=4)
        
        self.show_alert('Calibration Data Saved Successfully')

        self.resetInputs()

    def show_alert(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Alert")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def enableTableEditing(self):
        if self.calibrationTable.editTriggers() == QTableWidget.NoEditTriggers:
            self.calibrationTable.setEditTriggers(QTableWidget.AllEditTriggers)
            self.calibrationEditButton.setText('Save')
        else:
            self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.calibrationEditButton.setText('Edit')
        

    def resetInputs(self):
        self.fluidNameInput.setDisabled(False)  
        self.trialNoInput.setDisabled(False)
        self.fluidNameInput.clear()
        self.trialNoInput.clear()
        self.temperatureInput.clear()
        self.densityInput.clear()
        self.viscosityInput.clear()
        self.calibrationTable.setRowCount(0)
        self.inputsLocked = False  

    def calibrationGoBack(self):
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)

    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)

class ReportsPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(ReportsPageUI, self).__init__()
        loadUi("reportsPage.ui", self)

        self.mainUI = mainUI
        self.reportsBackButton.clicked.connect(self.reportsGoBack)

    def reportsGoBack(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI() 
    ui.show()
    sys.exit(app.exec_())