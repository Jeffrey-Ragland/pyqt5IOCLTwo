from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStackedWidget, QTableWidgetItem, QTableWidget, QHeaderView, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
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
        self.calibrationEditButton.clicked.connect(self.editAddedData)
        self.calibrationEditAllButton.clicked.connect(self.editAllData)
        self.calibrationSubmitButton.clicked.connect(self.submitAddedData)
        self.logoutButton.clicked.connect(self.logout)

        self.editAllMode = False

        self.inputsLocked = False
        self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)

        self.load_logo()
        

        self.calibrationTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def load_logo(self):
        pixmap = QPixmap('xymaLogoWhite.png')  

        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.xymaLogoLabel.setPixmap(resized_pixmap)
        self.xymaLogoLabel.setScaledContents(True)


    def populate_table_header(self):
        self.calibrationTable.setColumnCount(5)

        headers = ["Fluid Name", "Trial No", "Temperature", "Density", "Viscosity"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)


    def addToTable(self):
        self.populate_table_header()
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


    def submitAddedData(self): 

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
        
        self.show_alert('Calibration Data Added Successfully')

        self.resetInputs()


    def editAddedData(self):
        if self.calibrationTable.editTriggers() == QTableWidget.NoEditTriggers:
            self.calibrationTable.setEditTriggers(QTableWidget.AllEditTriggers)
            self.calibrationEditButton.setText('Save')
        else:
            self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.calibrationEditButton.setText('Edit')


    def editAllData(self):
        if not self.editAllMode:
            self.loadCalibrationData()
            self.calibrationTable.setEditTriggers(QTableWidget.AllEditTriggers)
            self.calibrationEditAllButton.setText('Save Changes')
            self.editAllMode = True
        else:
            self.saveEditedData()
            self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.calibrationEditAllButton.setText('Edit All')
            self.calibrationTable.setRowCount(0)
            self.editAllMode = False


    def loadCalibrationData(self):
        self.calibrationTable.setRowCount(0)
        self.calibrationTable.setColumnCount(3)

        headers = ["Fluid Name", "Edit", "Delete"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)

        calibrationJsonFile = 'calibrationData.json'

        try:
            with open(calibrationJsonFile, 'r') as file:
                calibrationFileData = json.load(file)
        except FileNotFoundError:
            self.show_alert('Calibration data file not found.')
            return

        for fluidName in calibrationFileData.keys():
            rowPosition = self.calibrationTable.rowCount()
            self.calibrationTable.insertRow(rowPosition)

            self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(fluidName))

            editButton = QPushButton("Edit")
            editButton.clicked.connect(lambda _, name=fluidName: self.loadTrials(name))
            self.calibrationTable.setCellWidget(rowPosition, 1, editButton)

            deleteButton = QPushButton("Delete")
            deleteButton.clicked.connect(lambda _, name=fluidName: self.deleteFluid(name))
            self.calibrationTable.setCellWidget(rowPosition, 2, deleteButton)


    def loadTrials(self, fluidName):
        self.calibrationTable.setRowCount(0)  # Clear the table
        self.calibrationTable.setColumnCount(3)

        headers = ["Trial No:", "Edit", "Delete"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)
        calibrationJsonFile = 'calibrationData.json'
        
        # Load the existing data
        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData:
            trials = calibrationFileData[fluidName]

            for trialNo in trials.keys():
                rowPosition = self.calibrationTable.rowCount()
                self.calibrationTable.insertRow(rowPosition)

                self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(trialNo))

                editButton = QPushButton("Edit")
                editButton.clicked.connect(lambda _, fluid=fluidName, trial=trialNo: self.loadReadings(fluid, trial))
                self.calibrationTable.setCellWidget(rowPosition, 1, editButton)

                deleteButton = QPushButton("Delete")
                deleteButton.clicked.connect(lambda _, fluid=fluidName, trial=trialNo: self.deleteTrial(fluid, trial))
                self.calibrationTable.setCellWidget(rowPosition, 2, deleteButton)


    def loadReadings(self, fluidName, trialNo):
        self.calibrationTable.setRowCount(0)  
        self.calibrationTable.setColumnCount(3)

        headers = ["Reading No:", "Edit", "Delete"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)

        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
            readings = calibrationFileData[fluidName][trialNo]

            for readingNo, reading in readings.items():
                rowPosition = self.calibrationTable.rowCount()
                self.calibrationTable.insertRow(rowPosition)

                self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(readingNo))

                editButton = QPushButton("Edit")
                editButton.clicked.connect(lambda _, fluid=fluidName, trial=trialNo, rNo=readingNo: self.editReading(fluid, trial, rNo))
                self.calibrationTable.setCellWidget(rowPosition, 1, editButton)

                deleteButton = QPushButton("Delete")
                deleteButton.clicked.connect(lambda _, fluid=fluidName, trial=trialNo, rNo=readingNo: self.deleteReading(fluid, trial, rNo))
                self.calibrationTable.setCellWidget(rowPosition, 2, deleteButton)


    def editReading(self, fluidName, trialNo, readingNo):
        self.calibrationTable.setRowCount(0)  
        self.calibrationTable.setColumnCount(4)

        headers = ["Temperature", "Density", "Viscosity", "Save"]
        self.calibrationTable.setHorizontalHeaderLabels(headers)

        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
            readings = calibrationFileData[fluidName][trialNo]
            if readingNo in readings:
                reading = readings[readingNo][0]  # Fetch the specific reading

                # Insert a new row for the editing process
                rowPosition = self.calibrationTable.rowCount()
                self.calibrationTable.insertRow(rowPosition)

                # Set the temperature, density, and viscosity values in the newly inserted row
                self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(str(reading["Temperature"])))
                self.calibrationTable.setItem(rowPosition, 1, QTableWidgetItem(str(reading["Density"])))
                self.calibrationTable.setItem(rowPosition, 2, QTableWidgetItem(str(reading["Viscosity"])))

                # Allow editing of the cells
                self.calibrationTable.setEditTriggers(QTableWidget.AllEditTriggers)

                # Create a Save button for this row
                saveButton = QPushButton("Save")
                saveButton.clicked.connect(lambda: self.saveReading(rowPosition, fluidName, trialNo, readingNo))
                self.calibrationTable.setCellWidget(rowPosition, 3, saveButton)


    
    # def saveReading(self, rowPosition, fluidName, trialNo, readingNo):
    # # Get the updated values from the table
    #     newTemperature = self.calibrationTable.item(rowPosition, 1).text()
    #     newDensity = self.calibrationTable.item(rowPosition, 2).text()
    #     newViscosity = self.calibrationTable.item(rowPosition, 3).text()

    #     # Load the current calibration data
    #     calibrationJsonFile = 'calibrationData.json'
    #     with open(calibrationJsonFile, 'r') as file:
    #         calibrationFileData = json.load(file)

    #     # Update the values in the data structure
    #     if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
    #         calibrationFileData[fluidName][trialNo][readingNo][0]["Temperature"] = newTemperature
    #         calibrationFileData[fluidName][trialNo][readingNo][0]["Density"] = newDensity
    #         calibrationFileData[fluidName][trialNo][readingNo][0]["Viscosity"] = newViscosity

    #     # Write the updated data back to the JSON file
    #     with open(calibrationJsonFile, 'w') as file:
    #         json.dump(calibrationFileData, file, indent=4)

    #     # Lock the fields again to prevent further editing
    #     self.calibrationTable.item(rowPosition, 1).setFlags(self.calibrationTable.item(rowPosition, 1).flags() & ~Qt.ItemIsEditable)
    #     self.calibrationTable.item(rowPosition, 2).setFlags(self.calibrationTable.item(rowPosition, 2).flags() & ~Qt.ItemIsEditable)
    #     self.calibrationTable.item(rowPosition, 3).setFlags(self.calibrationTable.item(rowPosition, 3).flags() & ~Qt.ItemIsEditable)

    #     # Replace Save button with Edit button again
    #     editButton = QPushButton("Edit")
    #     editButton.clicked.connect(lambda _, fluid=fluidName, trial=trialNo, rNo=readingNo: self.editReading(rowPosition, fluid, trial, rNo))
    #     self.calibrationTable.setCellWidget(rowPosition, 4, editButton)

    #     # Optionally show a message confirming the save action
    #     self.show_alert('Reading updated successfully!')


    def saveEditedData(self):
        calibrationJsonFile = 'calibrationData.json'

        try:
            with open(calibrationJsonFile, 'r') as file:
                calibrationFileData = json.load(file)
        except FileNotFoundError:
            calibrationFileData = {}

        updatedData = {}

        for row in range(self.calibrationTable.rowCount()):
            fluidName = self.calibrationTable.item(row, 0).text()
            trialNo = f"Trial{self.calibrationTable.item(row, 1).text()}"
            temperature = float(self.calibrationTable.item(row, 2).text())
            density = float(self.calibrationTable.item(row, 3).text())
            viscosity = float(self.calibrationTable.item(row, 4).text())

            reading_data = {"Temperature": temperature, "Density": density, "Viscosity": viscosity}

            if fluidName not in updatedData:
                updatedData[fluidName] = {}

            if trialNo not in updatedData[fluidName]:
                updatedData[fluidName][trialNo] = {}

            readingNo = 1
            while f'reading{readingNo}' in updatedData[fluidName][trialNo]:
                readingNo += 1

            updatedData[fluidName][trialNo][f'reading{readingNo}'] = [reading_data]

        for fluidName, trials in updatedData.items():
            if fluidName not in calibrationFileData:
                calibrationFileData[fluidName] = trials
            else:
                for trialNo, readings in trials.items():
                    if trialNo not in calibrationFileData[fluidName]:
                        calibrationFileData[fluidName][trialNo] = readings
                    else:
                        calibrationFileData[fluidName][trialNo].update(readings)

        with open(calibrationJsonFile, 'w') as file:
            json.dump(calibrationFileData, file, indent=4)

        self.show_alert('Calibration Data Edited Successfully')

    def resetInputs(self):
        self.fluidNameInput.setDisabled(False)  
        self.trialNoInput.setDisabled(False)
        self.fluidNameInput.clear()
        self.trialNoInput.clear()
        self.temperatureInput.clear()
        self.densityInput.clear()
        self.viscosityInput.clear()
        self.calibrationTable.setRowCount(0)
        self.calibrationTable.setColumnCount(0)
        self.inputsLocked = False

    def show_alert(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Alert")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()  

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