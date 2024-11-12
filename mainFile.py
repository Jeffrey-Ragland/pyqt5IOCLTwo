from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStackedWidget, QDialog, QButtonGroup
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt, QStandardPaths
import sys
import json
import time
import serial
import serial.tools.list_ports
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime
import pandas as pd
import os

class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        self.stackedWidget = QStackedWidget(self)
        self.setCentralWidget(self.stackedWidget)
        self.setWindowTitle('IOCL Software')
        self.setWindowIcon(QIcon('Assets/Images/xymaIcon.png'))
        
        self.client = None
        self.collection = None
        self.setup_mongodb()
        
        self.loginPage = LoginUI(self)
        self.mainPage = MainPageUI(self, collection = self.collection, serial_connection = None)

        self.stackedWidget.addWidget(self.loginPage)
        self.stackedWidget.addWidget(self.mainPage)
        
        self.stackedWidget.setCurrentWidget(self.loginPage)

        self.showMaximized()

        self.stackedWidget.currentChanged.connect(self.on_page_changed)

        self.check_serial_port()
        
    def setup_mongodb(self):
        try:
            self.client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
            db = self.client['IOCLDatabase']
            self.collection = db['fluidCollection']
            
            self.client.admin.command('ping')
            print('Connected to MongoDB!')
            
        except ServerSelectionTimeoutError:
            QMessageBox.warning(self, 'Database Connection Error', 'Failed to connect to the MongoDB server!')
            self.collection = None 

    def on_page_changed(self, index):
        current_page = self.stackedWidget.currentWidget()
        
        if current_page == self.mainPage:
            self.mainPage.start_serial_reading()
        else:
            self.mainPage.stop_serial_reading()

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
            
            self.mainPage.serial_connection = self.serial_connection
            
            self.stackedWidget.setCurrentWidget(self.loginPage)
            
        except serial.SerialException as e:
            QMessageBox.critical(self, "Serial Connection Error", f"Failed to establish serial connection: {str(e)}")
            sys.exit()
            
    def closeEvent(self, event):
        if self.serial_connection and self.serial_connection.is_open:
            print('Closing serial connection...')
            self.serial_connection.close()
            print('Serial connection terminated!')
            
        if self.client:
            print('Closing MongoDB connection...')
            self.client.close()
            print('MongoDB connection terminated!')
            
        event.accept()
            
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
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  

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
        
        
class StartButtonPopup(QDialog):
    def __init__(self, parent=None, collection=None):
        super(StartButtonPopup, self).__init__(parent)
        
        loadUi("Assets/UiFiles/startButtonPopup.ui",self)
        
        self.parent = parent
        self.collection = collection
        
        self.setWindowTitle('Fluid Entry')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.temperatureGroup = QButtonGroup(self)
        self.temperatureGroup.addButton(self.tempOpt1)
        self.temperatureGroup.addButton(self.tempOpt2)
        
        self.popupSubmitButton.clicked.connect(self.on_submit)
        self.popupCancelButton.clicked.connect(self.reject)
         
    def on_submit(self):
        
        fluid_name = self.fluidNameTextbox.text()
        selectedTemperature = None
        if self.tempOpt1.isChecked():
            selectedTemperature = 40
        elif self.tempOpt2.isChecked():
            selectedTemperature = 100
            
        if not fluid_name or selectedTemperature is None:
            QMessageBox.warning(self, 'Input Required', 'Please fill out all the fields!')
        else:
            entry = f"{fluid_name}-{selectedTemperature}"
            
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            dbEntry = {
                "FluidName": entry,
                "Density": self.parent.densityCardLabel.text(),
                "Viscosity": self.parent.viscosityCardLabel.text(),
                "Temperature": self.parent.temperatureCardLabel.text(),
                "Tandelta": self.parent.tandelta2CardLabel.text(),
                "WearDebris": self.parent.wearDebrisCardLabel.text(),
                "Timestamp": timestamp_str
            }
            
            try:
                self.collection.insert_one(dbEntry)
            except ServerSelectionTimeoutError:
                QMessageBox.warning(self, 'Database Connection Error', 'Failed to connect to the MongoDB server!')
                return
            
            try:
                with open("fluidData.json","r") as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
                
            if entry in data:
                QMessageBox.warning(self, 'Duplicate Entry', 'This fluid name and temperature already exists!')
            else:
                data.append(entry)

                with open ('fluidData.json', "w") as file:
                    json.dump(data, file, indent=4)

                print(f"Fluid Name: {fluid_name}, Temperature: {selectedTemperature}")
                self.accept()
   
class ReportsPopup(QDialog):
    def __init__(self, parent=None, collection=None):
        super(ReportsPopup, self).__init__(parent)
        
        loadUi("Assets/UiFiles/reportsPopup.ui",self)
        
        self.parent = parent
        self.collection = collection
        
        self.setWindowTitle('Download Reports')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.generateDropdownItems()
        
        self.reportsDownloadButton.clicked.connect(self.downloadReport)
        
    def generateDropdownItems(self):
        try:
            with open("fluidData.json", "r") as file:
                data = json.load(file)
                
                for entry in data:
                    self.fluidNameDropdown.addItem(entry)
                        
        except (FileNotFoundError, json.JSONDecodeError):
            print('Error reading the JSON file or the file is empty')
                    
    def downloadReport(self):
        selectedFluid = self.fluidNameDropdown.currentText()
        
        if self.collection is not None:
            try: 
                results = list(self.collection.find({"FluidName": selectedFluid}))
                
                if results:
                    df = pd.DataFrame(results)
                    
                    downloads_folder = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
                    
                    file_name = f"{selectedFluid}_report.xlsx"
                    file_path = os.path.join(downloads_folder, file_name)
                    
                    df.to_excel(file_path, index=False, engine='openpyxl')
                    
                    print("Excel file downloaded!")
                    
                else:
                    print(f"No records found for fluid: {selectedFluid}")
                    
            except Exception as e:
                print(f"Error retrieving data from MongoDB: {e}")
                
        else:
            print("Database connection is not available.")
        
        
# main page function
class MainPageUI(QMainWindow):
    def __init__(self, mainUI, collection, serial_connection):
        super(MainPageUI, self).__init__()
        loadUi("Assets/UiFiles/finalisedPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.collection = collection
        self.serial_connection = serial_connection
        
        self.testingLogoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.testingLogoutButton.setIconSize(QSize(40,40))
        
        # self.testingStopButton.setEnabled(False)
        
        self.testingLogoutButton.clicked.connect(self.logout)
        self.testingStartButton.clicked.connect(self.send_string_format)
        self.testingStopButton.clicked.connect(self.send_empty_string)
        self.reportsButton.clicked.connect(self.openReportsPopup)

        self.load_logo()
        
        self.serial_reader_thread = None

    def load_logo(self):
        pixmap = QPixmap('Assets/Images/xymaLogoWhite.png')  
        resized_pixmap = pixmap.scaled(150, 75, aspectRatioMode=1) 
        
        pixmap2 = QPixmap('Assets/Images/ioclRound.png')  
        resized_pixmap2 = pixmap2.scaled(75, 75, aspectRatioMode=1) 
        
        pixmap3 = QPixmap('Assets/Images/densityIcon.png')
        resized_pixmap3 = pixmap3.scaled(130, 130, aspectRatioMode=1) 
        
        pixmap4 = QPixmap('Assets/Images/viscosityIcon.png')
        resized_pixmap4 = pixmap4.scaled(130, 130, aspectRatioMode=1) 
        
        pixmap5 = QPixmap('Assets/Images/tempIcon.png')
        resized_pixmap5 = pixmap5.scaled(130, 130, aspectRatioMode=1) 
        
        pixmap7 = QPixmap('Assets/Images/tandeltaIcon2.png')
        resized_pixmap7 = pixmap7.scaled(130, 130, aspectRatioMode=1) 
        
        pixmap8 = QPixmap('Assets/Images/wearDebrisIcon.png')
        resized_pixmap8 = pixmap8.scaled(130, 130, aspectRatioMode=1) 
    
        self.XymaLogoLabel.setPixmap(resized_pixmap)
        self.XymaLogoLabel.setScaledContents(False)
        self.XymaLogoLabel.setAlignment(Qt.AlignCenter)
        
        self.IoclLogoLabel.setPixmap(resized_pixmap2)
        self.IoclLogoLabel.setScaledContents(False)
    
        self.densityCardIconLabel.setPixmap(resized_pixmap3)
        self.densityCardIconLabel.setScaledContents(False)
        self.densityCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.viscosityCardIconLabel.setPixmap(resized_pixmap4)
        self.viscosityCardIconLabel.setScaledContents(False)
        self.viscosityCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.temperatureCardIconLabel.setPixmap(resized_pixmap5)
        self.temperatureCardIconLabel.setScaledContents(False)
        self.temperatureCardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.tandelta2CardIconLabel.setPixmap(resized_pixmap7)
        self.tandelta2CardIconLabel.setScaledContents(False)
        self.tandelta2CardIconLabel.setAlignment(Qt.AlignCenter)
        
        self.wearDebrisCardIconLabel.setPixmap(resized_pixmap8)
        self.wearDebrisCardIconLabel.setScaledContents(False)
        self.wearDebrisCardIconLabel.setAlignment(Qt.AlignCenter)
        
    def openReportsPopup(self):
        try:
            with open("fluidData.json", "r") as file:
                data = json.load(file)
                
                if not data:
                    QMessageBox.warning(self, "No Data Available", 'Fluid entry is empty!')
                else:
                    dialog = ReportsPopup(self, collection = self.collection)
                    dialog.exec_()
                    
        except (FileNotFoundError, json.JSONDecodeError):
            print('Error reading the JSON file or the file is empty')
           
    def logout(self): 
       self.send_empty_string()
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)
       
    def send_string_format(self):
        if self.serial_connection:
            
            dialog = StartButtonPopup(self, collection=self.collection)
            
            if dialog.exec_() == QDialog.Accepted:
            
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
                print("Fluid entry canceled")
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
        # if 1 == 0 :
            print(f'Serial data received: {serial_data}')    
           
                        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI() 
    ui.show()
    sys.exit(app.exec_())