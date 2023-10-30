#!/usr/bin/env python3
import sys,os,platform,subprocess
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self,JDS=None):
        super().__init__()
        self.appName = ""
        self.bashcontent = ""
        self.applicationFName = ""
        self.containerImage = "root.sif"
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
        self.appLayout = QHBoxLayout()
        self.appLabel = QLabel("App Name :")
        self.appLineEdit = QLineEdit()
        self.appLineEdit.textChanged.connect(self.setAppName)
        self.appLayout.addWidget(self.appLabel)
        self.appLayout.addWidget(self.appLineEdit)


        self.bashLayout = QHBoxLayout()
        self.bashLayout2 = QHBoxLayout()
        self.bashLabel = QLabel("Preconfiguration bash script contents to run the application:")
        self.bashTextEdit = QTextEdit()
        self.bashTextEdit.setText("#!/bin/bash\nsource /cvmfs/cms.cern.ch/cmsset_default.sh")
        self.bashLayout.addWidget(self.bashLabel)
        self.bashLayout2.addWidget(self.bashTextEdit)
        

        self.applicationLayout = QHBoxLayout()
        self.applicationLabel = QLabel("Application File Name:")
        self.applicationLineEdit = QLineEdit()
        self.applicationButton = QPushButton("Open file")
        self.applicationButton.clicked.connect(self.openApplicationFile)
        self.applicationLayout.addWidget(self.applicationLabel)
        self.applicationLayout.addWidget(self.applicationLineEdit)
        self.applicationLayout.addWidget(self.applicationButton)

        self.containerLayout = QHBoxLayout()
        self.containerLabel = QLabel("Container Image File Name:")
        self.containerLineEdit = QLineEdit()
        self.containerButton = QPushButton("Open file")
        self.containerButton.clicked.connect(self.openContainerFile)
        self.containerLayout.addWidget(self.containerLabel)
        self.containerLayout.addWidget(self.containerLineEdit)
        self.containerLayout.addWidget(self.containerButton)

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

        self.jdlCustomLayout = QHBoxLayout()
        self.jdlCustomLayout2 = QHBoxLayout()
        self.jdlCustomLabel = QLabel("Custom line for JDL:")
        self.jdlCustomTextEdit = QTextEdit()
        self.jdlCustomTextEdit.setText("accounting_group= group_cms\n")
        self.jdlCustomLayout.addWidget(self.jdlCustomLabel)
        self.jdlCustomLayout2.addWidget(self.jdlCustomTextEdit)

        self.doneLayout = QHBoxLayout()
        self.doneButton = QPushButton("Done")
        self.doneButton.clicked.connect(self.writeJDL)
        self.doneLayout.addWidget(self.doneButton)
        

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.appLayout)
        self.layout.addLayout(self.bashLayout)
        self.layout.addLayout(self.bashLayout2)
        self.layout.addLayout(self.applicationLayout)
        self.layout.addLayout(self.containerLayout)
        self.layout.addLayout(self.fileListLayout)
        self.layout.addLayout(self.outputFileLayout)
        self.layout.addLayout(self.checkPointLayout)
        self.layout.addLayout(self.jdlCustomLayout)
        self.layout.addLayout(self.jdlCustomLayout2)

        self.layout.addLayout(self.doneLayout)
        self.setLayout(self.layout)

    def writeJDL(self):
        inputSandBox = "%s"%(self.applicationFName)
        if os.path.isfile("./LFNTool.py"):
            inputSandBox += ", LFNTool.py"
        jdl = f'''
JobBatchName            = {self.appName}_$(Cluster)
executable = run_{self.appName}.sh
universe   = container
requirements = ( HasSingularity == true )
getenv     = True
should_transfer_files = YES
Container_image = {self.containerImage}
output = job_$(Process).out
error = job_$(Process).err
log = job_$(Process).log
transfer_input_files = {inputSandBox}
transfer_output_files = {self.outputFname}
transfer_output_remaps = "{self.outputFname} = {self.outputRemapFname}"
when_to_transfer_output = ON_EXIT_OR_EVICT

'''
        if (self.checkPoint):
            jdl += f'''
transfer_checkpoint_files = checkpoint.tar.gz, state_running.txt 


KillSig= SIGUSR2
KillSigTimeout = 60
+SingularityExtraArgs= "--add-caps cap_checkpoint_restore"
checkpoint_exit_code = 85
+WantFTOnCheckpoint = True

notification = Error
notify_user = geonmo@kisti.re.kr

+WantFTOnCheckpoint = True
{ self.jdlCustomTextEdit.toPlainText() }
'''
            self.writeCheckPointExecutable()
        else:
            self.writeExecutable()
            jdl += f'''
{ self.jdlCustomTextEdit.toPlainText() }
'''
        if self.fileListFname == "":
            jdl += "queue 1"
        else:
            jdl += f'''
arguments  = $(DATAFile)
queue DATAFile from {self.fileListFname}'''
        f = open( self.appName+".sub","w")
        f.write(jdl)
        f.close()
        sys.exit(0)
    def writeCheckPointExecutable(self):
        appFName = self.applicationFName.split("/")[-1]
        with open(f"run_{self.appName}.sh","w") as f:
            runsh = '''
#!/bin/bash

trap ReceiveCheckPointSignal SIGUSR2

function ReceiveCheckPointSignal() {
        rm -rf "dumped_images-*"
        IMG_DIR="dumped_images-$(uuidgen)"
        mkdir ${IMG_DIR}
        /usr/local/sbin/criu dump --unprivileged -v4 -t ${TPID} -D $IMG_DIR -o criu.log
        tar -czvf checkpoint.tar.gz $IMG_DIR
        exit 85
}
if [ -s checkpoint.tar.gz ]; then
        tar -zxvf checkpoint.tar.gz
        IMG_DIR=$(echo dumped_images-*)
        /usr/local/sbin/criu restore --unprivileged -v4 -d -D $IMG_DIR

else
        if [ -z $TPID ]; then
                echo "Can not find {appFName}. Start script from begining"
                setsid ./{appFName} </dev/null &> /dev/null &
                TPID=$!
        else
                echo "Found {appFName}: $TPID"
        fi
'''
            runsh+='''
        while true
        do
                echo "Monitoring ${TPID} procces"
                kill -s 0 ${TPID}
                if [ $? -ne 0 ]; then
                   exit 0
                fi
                if [[ -e state_running.txt && $(tail -n1 state_running.txt) == "10" ]]; then
                        kill -SIGUSR2 $$
                        echo "Checkpoint!!" >> state_running.txt
                fi
                sleep 1
        done
fi
'''
            print(runsh)
            f.write(runsh)
            f.close()
    def writeExecutable(self):
        with open(f"run_{self.appName}.sh",'w') as f:
            f.write(self.bashTextEdit.toPlainText())
            f.write(f"\n{self.applicationFName} $1")
            f.close()
    def searchOutputFile(self):
        infile = open(self.applicationFName)
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
    def openContainerFile(self):
        self.containerImage = QFileDialog.getOpenFileName(self)[0]
        filename = self.containerImage.split("/")[-1]
        self.containerLineEdit.setText(filename)
    def openApplicationFile(self):
        scriptDialog = QFileDialog()
        dialogwindow = \
        scriptDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()","","All \
                Files (*);;Python Files (*.py);;ROOT Macro Files (*.C)")
        self.applicationFName = dialogwindow[0]
        filename = self.applicationFName.split("/")[-1]
        self.applicationLineEdit.setText(filename)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
