#!/usr/bin/env python3
import sys,os,platform,subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self,JDS=None):
        super().__init__()
        self.appName = ""
        self.execFname = ""
        self.scriptFName = ""
        self.fileListFname = ""
        self.arguements= ""
        self.outError =""
        self.transfer_input_files=""
        self.transfer_output_files=""
        self.outputFname=""
        self.outputRemapFname=""
        self.checkPoint = False
        if ( JDS is not None) : self.parseJDS(JDS)
        self.setupUI()

    def setupUI(self):
        #self.layout = QGridLayout()
        self.appLayout = QHBoxLayout()
        self.appLabel = QLabel("App Name :")
        self.appLineEdit = QLineEdit()
        self.appLineEdit.textChanged.connect(self.setAppName)
        #self.appProcessButton = QPushButton("$(Process)")
        #self.appProcessButton.clicked.connect(self.appAddProcess)
        self.appLayout.addWidget(self.appLabel)
        self.appLayout.addWidget(self.appLineEdit)
        #self.appLayout.addWidget(self.appProcessButton)

        self.executeLayout = QHBoxLayout()
        self.executeLabel = QLabel("Running Script File Name:")
        self.executeLineEdit = QLineEdit()
        self.executeButton = QPushButton("Open file")
        self.executeButton.clicked.connect(self.openExecuteFile)
        self.executeLayout.addWidget(self.executeLabel)
        self.executeLayout.addWidget(self.executeLineEdit)
        self.executeLayout.addWidget(self.executeButton)

        self.scriptLayout = QHBoxLayout()
        self.scriptLabel = QLabel("Analsis Code File Name:")
        self.scriptLineEdit = QLineEdit()
        self.scriptButton = QPushButton("Open file")
        self.scriptButton.clicked.connect(self.openScriptFile)
        self.scriptLayout.addWidget(self.scriptLabel)
        self.scriptLayout.addWidget(self.scriptLineEdit)
        self.scriptLayout.addWidget(self.scriptButton)

        self.fileListLayout = QHBoxLayout()
        self.fileListLabel = QLabel("FileList File Name:")
        self.fileListLineEdit = QLineEdit()
        self.fileListButton = QPushButton("Open file")
        self.fileListButton.clicked.connect(self.openFileListFile)
        self.fileListLayout.addWidget(self.fileListLabel)
        self.fileListLayout.addWidget(self.fileListLineEdit)
        self.fileListLayout.addWidget(self.fileListButton)

        self.outputFileLayout = QHBoxLayout()
        self.outputFileLabel = QLabel("output File Name:")
        self.outputFileLineEdit = QLineEdit()
        self.outputFileLineEdit.textChanged.connect(self.setOutputFileName)
        self.outputFileButton = QPushButton("Search")
        self.outputFileButton.clicked.connect(self.searchOutputFile)
        self.outputFileLayout.addWidget(self.outputFileLabel)
        self.outputFileLayout.addWidget(self.outputFileLineEdit)
        self.outputFileLayout.addWidget(self.outputFileButton)

        self.checkPointLayout = QHBoxLayout()
        self.checkPointLabel = QLabel("CheckPoint option:")
        self.checkPointCheckbox = QCheckBox("Enable CheckPoint",self)
        self.checkPointCheckbox.stateChanged.connect(self.setCheckPoint)
        self.checkPointLayout.addWidget(self.checkPointCheckbox)
 


        self.doneLayout = QHBoxLayout()
        self.doneButton = QPushButton("Done")
        self.doneButton.clicked.connect(self.writeJDL)
        self.doneLayout.addWidget(self.doneButton)
        

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.appLayout)
        self.layout.addLayout(self.executeLayout)
        self.layout.addLayout(self.scriptLayout)
        self.layout.addLayout(self.fileListLayout)
        self.layout.addLayout(self.outputFileLayout)
        self.layout.addLayout(self.checkPointLayout)
        self.layout.addLayout(self.doneLayout)
        self.setLayout(self.layout)

    def writeJDL(self):
        inputSandBox = "%s"%(self.scriptFname)
        if os.path.isfile("./LFNTool.py"):
            inputSandBox += ", LFNTool.py"
        jdl=f'''
batch_name = {self.appName}
executable = {self.execFname}
universe   = vanilla
arguments  = $(DATAFile)
getenv     = True

transfer_input_files = {inputSandBox}
should_transfer_files = YES
when_to_transfer_output = ON_EXIT

transfer_output_files = {self.outputFname}
transfer_output_remaps = "{self.outputFname} = {self.outputRemapFname}"


output = job_$(Process).out
error  = job_$(Process).err
log = condor.log

accounting_group=group_cms
'''
        print(f"checkpoint : {self.checkPoint}")
        if (self.checkPoint):
            jdl += f'''
KillSig= SIGUSR2
KillSigTimeout = 60
+SingularityExtraArgs= "--add-caps all"
checkpoint_exit_code = 85
+WantFTOnCheckpoint = True
'''
            self.writeCheckPointExecutable()
        jdl += '''
queue DATAFile from %s
'''%(self.fileListFname)
        f = open( self.appName+".sub","w")
        f.write(jdl)
        f.close()
        
        sys.exit(0)
    def writeCheckPointExecutable(self):
        with open(self.execFname) as f:
            lines = f.readlines()
    def searchOutputFile(self):
        infile = open(self.scriptFname)
        lines = infile.readlines()
        for line in lines :
            sline = line.strip()
            if ( sline.upper().find("RECREATE") != -1 ) :
                filename = sline.split("TFile")[-1].replace("RECREATE","").replace("recreate","").replace('"',"").replace(",","").replace("(","").replace(")","")
                msgBox = QMessageBox()
                msgBox.setText( "An output file name was found from analysis code.")
                msgBox.setInformativeText("Are you sure to use \"%s\" as output filename?"%(filename))
                msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msgBox.setDefaultButton(QMessageBox.Yes)
                ret = msgBox.exec()
                if ret == QMessageBox.Yes:
                    self.outputFileLineEdit.setText(filename)
                else:
                    pass

    def setOutputFileName(self):
        self.outputFname = self.outputFileLineEdit.text()
        name, ext = os.path.splitext(self.outputFname)
        self.outputRemapFname = name+"_"+"$(Process)"+ext

    def setAppName(self):
        self.appName = self.appLineEdit.text()

    def appAddProcess(self):
        self.appLineEdit.setText( self.appLineEdit.text() + "$(Process)")
    def setCheckPoint(self,state):
        print("Call setCheckpoint")
        if(state == Qt.Checked):
            print("enable checkpoint")
            self.checkPoint = True
        else:
            self.checkPoint = False
    def openFileListFile(self):
        self.fileListFname = QFileDialog.getOpenFileName(self)[0]
        filename = self.fileListFname.split("/")[-1]
        self.fileListLineEdit.setText(filename)
    def openExecuteFile(self):
        self.execFname = QFileDialog.getOpenFileName(self)[0]
        filename = self.execFname.split("/")[-1]
        self.executeLineEdit.setText(filename)
    def openScriptFile(self):
        scriptDialog = QFileDialog()
        dialogwindow = \
        scriptDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","","All \
                Files (*);;Python Files (*.py);;ROOT Macro Files (*.C)")
        self.scriptFname = dialogwindow[0]
        filename = self.scriptFname.split("/")[-1]
        self.scriptLineEdit.setText(filename)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
