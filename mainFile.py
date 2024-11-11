from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QStackedWidget, QPushButton, QDialog, QVBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QPushButton
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
        self.mainPage = MainPageUI(self, None)
        self.reportsPage = ReportsPageUI(self)

        self.stackedWidget.addWidget(self.loginPage)
        self.stackedWidget.addWidget(self.mainPage)
        self.stackedWidget.addWidget(self.reportsPage)
        
        self.stackedWidget.setCurrentWidget(self.loginPage)

        self.showMaximized()

        self.stackedWidget.currentChanged.connect(self.on_page_changed)

        self.check_serial_port()

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
    def __init__(self, parent=None):
        super(StartButtonPopup, self).__init__(parent)
        
        loadUi("Assets/UiFiles/startButtonPopup.ui",self)
        
        self.temperatureGroup = QButtonGroup(self)
        self.temperatureGroup.addButton(self.tempOpt1)
        self.temperatureGroup.addButton(self.tempOpt2)
        
        self.popupSubmitButton.clicked.connect(self.on_submit)
        self.popupCancelButton.clicked.connect(self.reject)
        
    def on_submit(self):
        fluid_name, temperature = self.get_values()
        
        print(f"Fluid Name: {fluid_name}, Temperature: {temperature}")
        
        self.accept()

    def get_values(self):
        fluid_name = self.fluidNameTextbox.text()
        temperature = None
        if self.tempOpt1.isChecked():
            temperature = 40
        elif self.tempOpt2.isChecked():
            temperature = 100
        return fluid_name, temperature

# main page function
class MainPageUI(QMainWindow):
    def __init__(self, mainUI, serial_connection):
        super(MainPageUI, self).__init__()
        loadUi("Assets/UiFiles/finalisedPage.ui", self)

        self.setStyleSheet("QMainWindow {"
                           "background-image: url('Assets/Images/homepage.png');"  
                           "background-position: center;"
                           "}")

        self.mainUI = mainUI
        self.serial_connection = serial_connection
        
        self.testingLogoutButton.setIcon(QIcon("Assets/Images/logoutIcon.png"))
        self.testingLogoutButton.setIconSize(QSize(40,40))
        
        # self.testingStopButton.setEnabled(False)
        
        self.testingLogoutButton.clicked.connect(self.logout)
        self.testingStartButton.clicked.connect(self.send_string_format)
        self.testingStopButton.clicked.connect(self.send_empty_string)
        self.reportsButton.clicked.connect(self.go_to_reports)

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
        
    def go_to_reports(self):
        self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.reportsPage)
    
    def logout(self): 
       self.send_empty_string()
       self.mainUI.stackedWidget.setCurrentWidget(self.mainUI.loginPage)
       
    def send_string_format(self):
        if self.serial_connection:
            
            dialog = StartButtonPopup(self)
            
            if dialog.exec_() == QDialog.Accepted:
                # Get the values from the dialog
                fluid_name, temperature = dialog.get_values()
                print(f"Fluid Name: {fluid_name}, Temperature: {temperature}")
            
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