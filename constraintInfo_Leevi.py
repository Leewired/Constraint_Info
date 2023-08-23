import maya.cmds as cmds
import pymel.core as pm
from PySide2 import QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from functools import partial


def _getMayaMainWindow():
    # this is to set up parenting the UI to mayas main window
    # get main window of maya (memory address)
    win = omui.MQtUtil_mainWindow()
    # pointer to wrapped instance
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
    return ptr


class viewConstraintsUI(QtWidgets.QWidget):

    def __init__(self):

        try:
            pm.deleteUI('constraints_info')
        except RuntimeError:
            print('No previous UI exists')

        parent = QtWidgets.QDialog(parent=_getMayaMainWindow())
        parent.setObjectName('constraints_info')
        parent.setWindowTitle("Constraints Info")
        layout = QtWidgets.QVBoxLayout(parent)

        super(viewConstraintsUI, self).__init__(parent=parent)
        obj, objCons, objPar, parCons = self._getBuildInfo()

        if obj:
            self._buildUI(obj=obj, obj_constraints_info=objCons, par=objPar, par_constraints_info=parCons)
            self.parent().layout().addWidget(self)
            parent.show()

    def _getBuildInfo(self):

        sel = cmds.ls(sl=True)
        par = cmds.listRelatives(parent=True)

        if len(sel) == 0 or len(sel) >= 2:
            cmds.confirmDialog(m="Select one object")
            cmds.warning('Select one object')
            return None
        else:
            print('Selected:\n')
            selItemConstraintsInfo = self.getConstraintsInfo(sel)

            obj = sel[0]
            objCons = selItemConstraintsInfo
            objPar = None
            parCons = None

            if par:
                print('\n\nParent:\n')
                parItemConstraintsInfo = self.getConstraintsInfo(par)

                objPar = par[0]

                if parItemConstraintsInfo:
                    parCons = parItemConstraintsInfo

            return obj, objCons, objPar, parCons

    def getConstraintsInfo(self, obj):

        cons = cmds.listRelatives(obj, type='constraint')
        itemsConstraints = {}

        if not cons:
            print('\tNo constraints found for %s' % obj[0])
        else:
            for con in cons:
                conTargets = set(cmds.listConnections(con + '.target'))
                conTargets.remove(con)
                itemsConstraints.update({con: conTargets})

            lines = ['\tObject: %s' % obj[0], '\tObject constraints: ']
            for s in itemsConstraints:
                lines.append('\t\t' + s)
                n = 1
                for t in itemsConstraints.get(s):
                    lines.append('\t\t\tTarget %s: %s' % (n, t))
                    n += 1
            result = '\n'.join(lines)
            print(result)
            return itemsConstraints

    def select(self, obj):
        cmds.select(obj)

    def _buildUI(self, obj=None, obj_constraints_info=None, par=None, par_constraints_info=None):

        layout = QtWidgets.QGridLayout(self)
        row = 0
        column = 0
        conAmount = 0

        if obj_constraints_info or par_constraints_info:
            try:
                conAmount = len(obj_constraints_info)
            except TypeError:
                conAmount = len(par_constraints_info)

        if obj_constraints_info and par_constraints_info:
            conAmount = [len(obj_constraints_info) if len(obj_constraints_info) >= len(par_constraints_info) else len(par_constraints_info)][0]

        selWidget = self._buildFromObject(obj=obj, obj_constraints_info=obj_constraints_info, title='Selected Object')
        layout.addWidget(selWidget, row, column, 1, conAmount)
        row += 1

        parWidget = self._buildFromObject(obj=par, obj_constraints_info=par_constraints_info, title='Parent Object')
        layout.addWidget(parWidget, row, column, 1, conAmount)

    def _buildFromObject(self, obj=None, obj_constraints_info=None, title=None):

        boxRow = 0
        vBoxRow = 0
        gridRow = 0
        column = 0

        selGroupBox = QtWidgets.QGroupBox(title)
        boxRow += 1

        selLayout = QtWidgets.QVBoxLayout()
        selGroupBox.setLayout(selLayout)

        if obj:
            objBtn = QtWidgets.QPushButton()
            objBtn.setText(obj)
            objBtn.clicked.connect(partial(self.select, obj))
            selLayout.addWidget(objBtn, vBoxRow)
            vBoxRow += 1

            conLabel = QtWidgets.QLabel()
            conLabel.setText('Constraints:')
            conLabel.setAlignment(QtCore.Qt.AlignCenter)
            selLayout.addWidget(conLabel, vBoxRow)
            vBoxRow += 1

            selConLayout = QtWidgets.QGridLayout()
            selLayout.addLayout(selConLayout, vBoxRow)

            if obj_constraints_info:

                for oc in obj_constraints_info:
                    SelConBtn = QtWidgets.QPushButton()
                    SelConBtn.setText(oc)
                    SelConBtn.clicked.connect(partial(self.select, oc))
                    selConLayout.addWidget(SelConBtn, gridRow, column)
                    gridRow += 1

                    selConTargLabel = QtWidgets.QLabel()
                    selConTargLabel.setText('Constrained to:')
                    selConTargLabel.setAlignment(QtCore.Qt.AlignCenter)
                    selConLayout.addWidget(selConTargLabel, gridRow, column)
                    gridRow += 1

                    for ocTarget in obj_constraints_info.get(oc):

                        SelConTargBtn = QtWidgets.QPushButton()
                        SelConTargBtn.setText(ocTarget)
                        SelConTargBtn.clicked.connect(partial(self.select, ocTarget))
                        selConLayout.addWidget(SelConTargBtn, gridRow, column)
                        gridRow += 1

                    gridRow = 0
                    column += 1

            else:
                SelConBtn = QtWidgets.QLabel()
                SelConBtn.setText('No Constraints')
                SelConBtn.setAlignment(QtCore.Qt.AlignCenter)
                selConLayout.addWidget(SelConBtn, gridRow, column)

        else:
            objBtn = QtWidgets.QLabel()
            objBtn.setText('None')
            objBtn.setAlignment(QtCore.Qt.AlignCenter)
            selLayout.addWidget(objBtn, vBoxRow)

        return selGroupBox
