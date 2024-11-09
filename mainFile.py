from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStackedWidget, QTableWidgetItem, QTableWidget, QHeaderView, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
import sys
import json
import time
import serial
import serial.tools.list_ports

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)
        self.setWindowTitle('IOCL Software')
        self.setWindowIcon(QIcon('Assets/Images/xymaIcon.png'))

        self.loginPage = LoginUI(self)
        self.mainPage = MainPageUI(self)
        self.testingPage = TestingPageUI(self, None)
        self.calibrationMenuPage = CalibrationMenuPageUI(self)
        self.manualCalibrationPage = ManualCalibrationPageUI(self)
        self.waveguideCalibrationPage = WaveguideCalibrationPageUI(self)
        self.reportsPage = ReportsPageUI(self)

        self.stackedWidget.addWidget(self.loginPage)
        self.stackedWidget.addWidget(self.mainPage)
        self.stackedWidget.addWidget(self.testingPage)
        self.stackedWidget.addWidget(self.calibrationMenuPage)
        self.stackedWidget.addWidget(self.manualCalibrationPage)
        self.stackedWidget.addWidget(self.waveguideCalibrationPage)
        self.stackedWidget.addWidget(self.reportsPage)
        
        self.stackedWidget.setCurrentWidget(self.loginPage)

        self.showMaximized()

        self.stackedWidget.currentChanged.connect(self.on_page_changed)

        # self.check_serial_port()

    def on_page_changed(self, index):
        current_page = self.stackedWidget.currentWidget()
        
        if current_page == self.testingPage:
            self.testingPage.start_serial_reading()
        else:
            self.testingPage.stop_serial_reading()

        if isinstance(current_page, LoginUI):
            self.showMaximized()  
        else:
            self.showFullScreen() 

    def check_serial_port(self):
        
        ports = serial.tools.list_ports.comports()

        usbPorts = []

        for port in ports:
            if 'USB' in port.description:
                usbPorts.append(port.device)

        if usbPorts:
            self.port_name = usbPorts[0]
            print(f"USB Serial Port found: {self.port_name}")
            self.establish_serial_connection()

        else:
            QMessageBox.critical(self, "Port Not Availabe", "No USB serial port found. The application cannot proceed!")
            sys.exit()
            
    def establish_serial_connection(self):
        try:
            self.serial_connection = serial.Serial(self.port_name, 230400)
            print(f"Serial connection established on {self.port_name}")
            
            self.testingPage.serial_connection = self.serial_connection
            
            self.stackedWidget.setCurrentWidget(self.loginPage)
            
        except serial.SerialException as e:
            QMessageBox.critical(self, "Serial Connection Error", f"Failed to establish serial connection: {str(e)}")
            sys.exit()
            
    # def closeEvent(self, event):
    #     if self.serial_connection and self.serial_connection.is_open:
    #         print('Closing serial connection...')
    #         self.serial_connection.close()
    #         print('Serial connection terminated!')
            
    #     event.accept()
            
class LoginUI(QMainWindow):
    def __init__(self, mainUI):
        super(LoginUI, self).__init__()

        loadUi("Assets/UiFiles/newLogin.ui",self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/loginCover.jpg');"  
                           "background-position: center;"
                           "}")

        self.loginButton.clicked.connect(self.check_credentials)
        self.mainUI = mainUI

        self.correct_email = "a"
        self.correct_password = "a"

        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoBlue.png')  

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
        loadUi("Assets/UiFiles/mainPage.ui", self) 

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.logoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.logoutButton.setIconSize(QSize(32,32))
        self.logoutButton.clicked.connect(self.logout)
        
        self.testingButton.clicked.connect(self.GoToTestingPage)
        # self.testingIconLabel.clicked.connect(self.GoToTestingPage)
        
        self.calibrationButton.clicked.connect(self.GoToCalibrationMenuPage)
        self.reportsButton.clicked.connect(self.GoToReportsPage)

        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')
        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
        
        pixmap2 = QPixmap('Assets/Images/testingIcon.png')
        resized_pixmap2 = pixmap2.scaled(100, 120, aspectRatioMode=1)
        
        pixmap3 = QPixmap('Assets/Images/calibrationIcon.png')
        resized_pixmap3 = pixmap3.scaled(100, 120, aspectRatioMode=1)
        
        pixmap4 = QPixmap('Assets/Images/reportsIcon.png')
        resized_pixmap4 = pixmap4.scaled(100, 120, aspectRatioMode=1)
    
        self.mainpageXymaLogoLabel.setPixmap(resized_pixmap)
        self.mainpageXymaLogoLabel.setScaledContents(True)
        
        self.testingIconLabel.setPixmap(resized_pixmap2)
        self.testingIconLabel.setScaledContents(False)
        self.testingIconLabel.setAlignment(Qt.AlignCenter)
        
        self.calibrationIconLabel.setPixmap(resized_pixmap3)
        self.calibrationIconLabel.setScaledContents(False)
        self.calibrationIconLabel.setAlignment(Qt.AlignCenter)
        
        self.reportsIconLabel.setPixmap(resized_pixmap4)
        self.reportsIconLabel.setScaledContents(False)
        self.reportsIconLabel.setAlignment(Qt.AlignCenter)

    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)

    def GoToTestingPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.testingPage)

    def GoToCalibrationMenuPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.calibrationMenuPage)

    def GoToReportsPage(self):
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.reportsPage)
       
# serial reading thread in testing page    
class SerialReaderThread(QThread):
    data_received = pyqtSignal(str)
    
    def __init__(self, serial_connection):
        super(SerialReaderThread, self).__init__()
        self.serial_connection = serial_connection
        self.running = True
    
    def run(self):
        while self.running:
            if self.serial_connection and self.serial_connection.in_waiting > 0:
                serialData = self.serial_connection.readline().decode('utf-8').strip()
                if serialData:
                    self.data_received.emit(serialData)
                else:
                    self.msleep(10)
                    
    def stop(self):
        self.running = False
        self.quit()
        self.wait()

# testing page function
class TestingPageUI(QMainWindow):
    def __init__(self, mainUI, serial_connection):
        super(TestingPageUI, self).__init__()
        loadUi("Assets/UiFiles/testingPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.serial_connection = serial_connection
        
        self.testingBackButton.setIcon(QIcon("Assets/Images/backIcon.png"))
        self.testingBackButton.setIconSize(QSize(32,32))
        self.testingLogoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.testingLogoutButton.setIconSize(QSize(32,32))
        
        # self.testingStopButton.setEnabled(False)
        
        self.testingBackButton.clicked.connect(self.testingGoBack)
        self.testingLogoutButton.clicked.connect(self.logout)
        self.testingStartButton.clicked.connect(self.send_string_format)
        self.testingStopButton.clicked.connect(self.send_empty_string)

        self.load_logo()
        
        self.serial_reader_thread = None

    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  
        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
        
        pixmap2 = QPixmap('Assets/Images/portsImage.png')
        resized_pixmap2 = pixmap2.scaled(300, 720, aspectRatioMode=1) 
        
        pixmap3 = QPixmap('Assets/Images/densityIcon.png')
        resized_pixmap3 = pixmap3.scaled(80, 80, aspectRatioMode=1) 
        
        pixmap4 = QPixmap('Assets/Images/viscosityIcon.png')
        resized_pixmap4 = pixmap4.scaled(80, 80, aspectRatioMode=1) 
        
        pixmap5 = QPixmap('Assets/Images/tempIcon.png')
        resized_pixmap5 = pixmap5.scaled(80, 80, aspectRatioMode=1) 
        
        pixmap6 = QPixmap('Assets/Images/tandeltaIcon1.png')
        resized_pixmap6 = pixmap6.scaled(80, 80, aspectRatioMode=1) 
        
        pixmap7 = QPixmap('Assets/Images/tandeltaIcon2.png')
        resized_pixmap7 = pixmap7.scaled(80, 80, aspectRatioMode=1) 
        
        pixmap8 = QPixmap('Assets/Images/wearDebrisIcon.png')
        resized_pixmap8 = pixmap8.scaled(80, 80, aspectRatioMode=1) 
    
        self.XymaLogoLabel.setPixmap(resized_pixmap)
        self.XymaLogoLabel.setScaledContents(True)
        
        self.portsImageLabel.setPixmap(resized_pixmap2)
        self.portsImageLabel.setScaledContents(False)
        self.portsImageLabel.setAlignment(Qt.AlignCenter)
        
        self.densityCardIconLabel.setPixmap(resized_pixmap3)
        self.densityCardIconLabel.setScaledContents(False)
        self.densityCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.viscosityCardIconLabel.setPixmap(resized_pixmap4)
        self.viscosityCardIconLabel.setScaledContents(False)
        self.viscosityCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.temperatureCardIconLabel.setPixmap(resized_pixmap5)
        self.temperatureCardIconLabel.setScaledContents(False)
        self.temperatureCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.tandelta1CardIconLabel.setPixmap(resized_pixmap6)
        self.tandelta1CardIconLabel.setScaledContents(False)
        self.tandelta1CardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.tandelta2CardIconLabel.setPixmap(resized_pixmap7)
        self.tandelta2CardIconLabel.setScaledContents(False)
        self.tandelta2CardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.wearDebrisCardIconLabel.setPixmap(resized_pixmap8)
        self.wearDebrisCardIconLabel.setScaledContents(False)
        self.wearDebrisCardIconLabel.setAlignment(Qt.AlignCenter)
        

    def testingGoBack(self):
       self.send_empty_string()
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)

    def logout(self): 
       self.send_empty_string()
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)
       
    def send_string_format(self):
        if self.serial_connection:
            data = "\n"
            print(f"String format sent: {data}")
            self.serial_connection.write(data.encode())
            time.sleep(0.5)
            
            data = "(1,0,0,2.0,200000,50,2,7,4,200000,0,100,4,1,0)"
            print(f"String format sent: {data}")
            self.serial_connection.write(data.encode())
            
            # self.testingStartButton.setEnabled(False)
            # self.testingStopButton.setEnabled(True)
        else:
            print('Serial connection not established')
            
    def send_empty_string(self):
        if self.serial_connection:
            data = "\n"
            print(f"String format sent: {data}")
            self.serial_connection.write(data.encode())
            
            # self.testingStartButton.setEnabled(True)
            # self.testingStopButton.setEnabled(False)
        else:
            print('Serial connection not established')
                
    def start_serial_reading(self):
        if self.serial_connection:
            self.serial_reader_thread = SerialReaderThread(self.serial_connection)
            self.serial_reader_thread.data_received.connect(self.on_data_received)
            self.serial_reader_thread.start()
            print('Serial reading started')
            
    def stop_serial_reading(self):
        if self.serial_reader_thread:
            self.serial_reader_thread.stop()
            print('Serial reading stopped')

    def on_data_received(self, serial_data):
        print(f'Serial data received: {serial_data}')    

class CalibrationMenuPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(CalibrationMenuPageUI, self).__init__()
        loadUi("Assets/UiFiles/calibrationMenuPage.ui", self)
        
        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")
        
        self.mainUI = mainUI
        self.calibrationMenuBackButton.setIcon(QIcon("Assets/Images/backIcon.png"))
        self.calibrationMenuBackButton.setIconSize(QSize(32,32))
        self.calibrationMenuLogoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.calibrationMenuLogoutButton.setIconSize(QSize(32,32))
        
        self.manualCalibrationButton.clicked.connect(self.goToMaualCalibrationPage)
        self.waveguideCalibrationButton.clicked.connect(self.goToWaveguideCalibrationPage)
        self.calibrationMenuBackButton.clicked.connect(self.goToMainMenu)
        self.calibrationMenuLogoutButton.clicked.connect(self.logout)
        
        
        self.load_logo()

    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  
        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
        
        pixmap2 = QPixmap('Assets/Images/manualCalibrationIcon.png')  
        resized_pixmap2 = pixmap2.scaled(120, 120, aspectRatioMode=1) 
        
        pixmap3 = QPixmap('Assets/Images/waveguideCalibrationIcon.png')  
        resized_pixmap3 = pixmap3.scaled(120, 120, aspectRatioMode=1) 
    
        self.XymaLogoLabel.setPixmap(resized_pixmap)
        self.XymaLogoLabel.setScaledContents(True)
        
        self.manualCalibrationIconLabel.setPixmap(resized_pixmap2)
        self.manualCalibrationIconLabel.setScaledContents(False)
        self.manualCalibrationIconLabel.setAlignment(Qt.AlignCenter)
        
        self.waveguideCalibrationIconLabel.setPixmap(resized_pixmap3)
        self.waveguideCalibrationIconLabel.setScaledContents(False)
        self.waveguideCalibrationIconLabel.setAlignment(Qt.AlignCenter)
        
    def goToMaualCalibrationPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.manualCalibrationPage)
        
    def goToWaveguideCalibrationPage(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.waveguideCalibrationPage)
        
    def goToMainMenu(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)  
        
    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)  
                
# calibration page
class ManualCalibrationPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(ManualCalibrationPageUI, self).__init__()
        loadUi("Assets/UiFiles/manualCalibrationPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        
        self.calibrationBackButton.setIcon(QIcon("Assets/Images/backIcon.png"))
        self.calibrationBackButton.setIconSize(QSize(32,32))
        self.logoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.logoutButton.setIconSize(QSize(32,32))

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
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  

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
        
        oilStatus = None
        if self.freshRadioButton.isChecked():
            oilStatus = self.freshRadioButton.text()
        elif self.usedRadioButton.isChecked():
            oilStatus = self.usedRadioButton.text()

        if not fluidName or not trialNo or temperature is None or density is None or viscosity is None or oilStatus is None:
            self.show_alert("Please fill in all fields before adding.")
            return
        
        fluidName = fluidName + "-" + oilStatus 

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
            self.freshRadioButton.setDisabled(True)
            self.usedRadioButton.setDisabled(True)
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
            self.calibrationEditAllButton.setText('Done')
            self.editAllMode = True
        else:
            self.closeEditAllUI()
            self.calibrationTable.setEditTriggers(QTableWidget.NoEditTriggers)
            self.calibrationEditAllButton.setText('Edit All')
            self.calibrationTable.setRowCount(0)
            self.editAllMode = False


    def loadCalibrationData(self):
        self.calibrationTable.setRowCount(0)
        self.calibrationTable.setColumnCount(3)

        headers = ["Fluid Name", "", ""]
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

        headers = ["Trial No:", "", ""]
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

        headers = ["Reading No:", "", ""]
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

        headers = ["Temperature", "Density", "Viscosity", ""]
        self.calibrationTable.setHorizontalHeaderLabels(headers)

        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
            readings = calibrationFileData[fluidName][trialNo]
            if readingNo in readings:
                reading = readings[readingNo][0] 

                rowPosition = self.calibrationTable.rowCount()
                self.calibrationTable.insertRow(rowPosition)

                self.calibrationTable.setItem(rowPosition, 0, QTableWidgetItem(str(reading["Temperature"])))
                self.calibrationTable.setItem(rowPosition, 1, QTableWidgetItem(str(reading["Density"])))
                self.calibrationTable.setItem(rowPosition, 2, QTableWidgetItem(str(reading["Viscosity"])))

                self.calibrationTable.setEditTriggers(QTableWidget.AllEditTriggers)

                saveButton = QPushButton("Save")
                saveButton.clicked.connect(lambda: self.saveEditedReading(rowPosition, fluidName, trialNo, readingNo))
                self.calibrationTable.setCellWidget(rowPosition, 3, saveButton)


    def saveEditedReading(self, rowPosition, fluidName, trialNo, readingNo):

        temperature = self.calibrationTable.item(rowPosition, 0).text()
        density = self.calibrationTable.item(rowPosition, 1).text()
        viscosity = self.calibrationTable.item(rowPosition, 2).text()

        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
            readings = calibrationFileData[fluidName][trialNo]
            if readingNo in readings:
                readings[readingNo][0] = {
                "Temperature": float(temperature),
                "Density": float(density),
                "Viscosity": float(viscosity)
            }

        with open(calibrationJsonFile, 'w') as file:
            json.dump(calibrationFileData, file, indent=4)

        self.show_alert('Reading updated successfully!')
        self.loadReadings(fluidName, trialNo)


    def deleteFluid(self, fluidName):
        calibrationJsonFile = 'calibrationData.json'
    
        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData:
            del calibrationFileData[fluidName]

            with open(calibrationJsonFile, 'w') as file:
                json.dump(calibrationFileData, file, indent=4)

            self.show_alert(f'{fluidName} deleted successfully!')
            self.loadCalibrationData()


    def deleteTrial(self, fluidName, trialNo):
        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if fluidName in calibrationFileData and trialNo in calibrationFileData[fluidName]:
            del calibrationFileData[fluidName][trialNo] 

            if not calibrationFileData[fluidName]:
                del calibrationFileData[fluidName]

            with open(calibrationJsonFile, 'w') as file:
                json.dump(calibrationFileData, file, indent=4)

            self.show_alert(f'{trialNo} of {fluidName} deleted successfully!')
            self.loadTrials(fluidName) 


    def deleteReading(self, fluidName, trialNo, readingNo):
        calibrationJsonFile = 'calibrationData.json'

        with open(calibrationJsonFile, 'r') as file:
            calibrationFileData = json.load(file)

        if (fluidName in calibrationFileData and 
                trialNo in calibrationFileData[fluidName] and 
                readingNo in calibrationFileData[fluidName][trialNo]):
            del calibrationFileData[fluidName][trialNo][readingNo] 

            if not calibrationFileData[fluidName][trialNo]:
                del calibrationFileData[fluidName][trialNo]

            if not calibrationFileData[fluidName]:
                del calibrationFileData[fluidName]

            with open(calibrationJsonFile, 'w') as file:
                json.dump(calibrationFileData, file, indent=4)

            self.show_alert(f'{readingNo} of {trialNo} for {fluidName} deleted successfully!')
            self.loadReadings(fluidName, trialNo) 
    

    def closeEditAllUI(self):
        self.calibrationTable.setRowCount(0)  
        self.calibrationTable.setColumnCount(0)
        

    def resetInputs(self):
        self.fluidNameInput.setDisabled(False)  
        self.trialNoInput.setDisabled(False)
        self.freshRadioButton.setDisabled(False)
        self.usedRadioButton.setDisabled(False)
        self.fluidNameInput.clear()
        self.trialNoInput.clear()
        # resetting the radio button ->
        self.freshRadioButton.setAutoExclusive(False)
        self.usedRadioButton.setAutoExclusive(False)
        self.freshRadioButton.setChecked(False)
        self.usedRadioButton.setChecked(False)
        self.freshRadioButton.setAutoExclusive(True)
        self.usedRadioButton.setAutoExclusive(True)
        # <-
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
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.calibrationMenuPage)

    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)

class WaveguideCalibrationPageUI(QMainWindow):
    def __init__(self, MainUI):
        super(WaveguideCalibrationPageUI, self).__init__()
        loadUi("Assets/UiFiles/waveguideCalibrationPage.ui", self)
        
        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")
        
        self.mainUI = MainUI
        
        self.waveguideBackButton.setIcon(QIcon("Assets/Images/backIcon.png"))
        self.waveguideBackButton.setIconSize(QSize(32,32))
        self.waveguideLogoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.waveguideLogoutButton.setIconSize(QSize(32,32))
        
        self.waveguideBackButton.clicked.connect(self.goToCalibrationMenu)
        self.waveguideLogoutButton.clicked.connect(self.logout)
        
        self.load_logo()
        
    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  

        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.XymaLogoLabel.setPixmap(resized_pixmap)
        self.XymaLogoLabel.setScaledContents(True)
        
    def goToCalibrationMenu(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.calibrationMenuPage)
        
    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)  
        
class ReportsPageUI(QMainWindow):
    def __init__(self, mainUI):
        super(ReportsPageUI, self).__init__()
        loadUi("Assets/UiFiles/reportsPage.ui", self)
        
        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        
        self.reportsBackButton.setIcon(QIcon("Assets/Images/backIcon.png"))
        self.reportsBackButton.setIconSize(QSize(32,32))
        self.logoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.logoutButton.setIconSize(QSize(32,32))
        
        self.reportsBackButton.clicked.connect(self.reportsGoBack)
        self.logoutButton.clicked.connect(self.logout)
        
        self.load_logo()
        
    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  

        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
    
        self.xymaLogo.setPixmap(resized_pixmap)
        self.xymaLogo.setScaledContents(True)

    def reportsGoBack(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.mainPage)
        
    def logout(self): 
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)  

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI() 
    ui.show()
    sys.exit(app.exec_())