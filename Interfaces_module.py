import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QComboBox, QLineEdit, QDoubleSpinBox, QVBoxLayout,
    QLabel, QPushButton, QDateEdit, QSpinBox, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class RocketSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.resetWidgets()

    def initUI(self):
        self.setWindowTitle('I.L.O.N.G.M.A Interfaces')
        self.setWindowIcon(QIcon('ILONGMA.png'))
        self.setGeometry(0, 0, 300, 1000)
        self.setFixedSize(300, 1000)

        self.mainLayout = QVBoxLayout()

        self.maxSpeedLabel = QLabel('Max Speed (km/s):')
        self.setFixedFontSize(self.maxSpeedLabel, 10)
        self.maxSpeedSpinBox = QDoubleSpinBox()
        self.maxSpeedSpinBox.setRange(1, 10000)
        self.maxSpeedSpinBox.setSuffix(' km/s')
        self.maxSpeedSpinBox.setDecimals(2)
        self.setFixedFontSize(self.maxSpeedSpinBox, 10)

        self.orbitLabel = QLabel('Orbital Semi-Major Axis (km):')
        self.setFixedFontSize(self.orbitLabel, 10)
        self.orbitSpinBox = QDoubleSpinBox()
        self.orbitSpinBox.setRange(160, 35786)
        self.orbitSpinBox.setSuffix(' km')
        self.orbitSpinBox.setDecimals(2)
        self.setFixedFontSize(self.orbitSpinBox, 10)

        self.returnStatusLabel = QLabel('Return Status:')
        self.setFixedFontSize(self.returnStatusLabel, 10)
        self.returnStatusComboBox = QComboBox()
        self.returnStatusComboBox.addItems(['Return', 'Discard', 'Recycle'])
        self.setFixedFontSize(self.returnStatusComboBox, 10)

        self.launchDelayLabel = QLabel('Launch Delay (minutes):')
        self.setFixedFontSize(self.launchDelayLabel, 10)
        self.launchDelaySpinBox = QDoubleSpinBox()
        self.launchDelaySpinBox.setRange(0, 1440)
        self.launchDelaySpinBox.setDecimals(2)
        self.setFixedFontSize(self.launchDelaySpinBox, 10)

        self.launchDateLabel = QLabel('Launch Date:')
        self.setFixedFontSize(self.launchDateLabel, 10)
        self.launchDateEdit = QDateEdit()
        self.launchDateEdit.setCalendarPopup(True)
        self.setFixedFontSize(self.launchDateEdit, 10)

        self.launchAngleLabel = QLabel('Launch Angle (degrees):')
        self.setFixedFontSize(self.launchAngleLabel, 10)
        self.launchAngleSpinBox = QDoubleSpinBox()
        self.launchAngleSpinBox.setRange(0, 90)
        self.launchAngleSpinBox.setSuffix('°')
        self.launchAngleSpinBox.setDecimals(2)
        self.setFixedFontSize(self.launchAngleSpinBox, 10)

        self.rocketSelectionLabel = QLabel('Select Rocket Type:')
        self.setFixedFontSize(self.rocketSelectionLabel, 10)
        self.rocketComboBox = QComboBox()
        self.rocketComboBox.addItems([
            "SpaceX Falcon 9", "SpaceX Falcon Heavy", "SpaceX Falcon 9 Block 5", "SpaceX Starship",
            "Space Shuttle", "Saturn V", "Atlas V", "Delta IV Heavy", "Ariane 5", "Soyuz", "Proton-M",
            "Long March 5", "H-IIA", "H-IIB", "GSLV Mk III", "Electron", "Astra Rocket 3", "Falcon Heavy Block 5",
            "Saturn IB", "Falcon 1", "SLS (Space Launch System)", "Customize"
        ])
        self.setFixedFontSize(self.rocketComboBox, 10)
        self.rocketComboBox.currentIndexChanged.connect(self.handleRocketSelection)

        self.fuelTankCountLabel = QLabel('Number of Fuel Tanks:')
        self.setFixedFontSize(self.fuelTankCountLabel, 10)
        self.fuelTankCountSpinBox = QSpinBox()
        self.fuelTankCountSpinBox.setRange(1, 10)
        self.setFixedFontSize(self.fuelTankCountSpinBox, 10)

        self.fuelTankCountButton = QPushButton('Set Fuel Tanks')
        self.fuelTankCountButton.clicked.connect(self.createPropellantWidgets)
        self.setFixedFontSize(self.fuelTankCountButton, 10)

        self.customizationLayout = QVBoxLayout()
        self.customizationLayout.addWidget(QLabel('Rocket Name:'))
        self.rocketNameInput = QLineEdit()
        self.setFixedFontSize(self.rocketNameInput, 10)
        self.customizationLayout.addWidget(self.rocketNameInput)

        self.customizationLayout.addWidget(self.fuelTankCountLabel)
        self.customizationLayout.addWidget(self.fuelTankCountSpinBox)
        self.customizationLayout.addWidget(self.fuelTankCountButton)

        self.customizationLayout.addWidget(QLabel('Material:'))
        self.materialComboBox = QComboBox()
        self.materialComboBox.addItems(["Aluminum", "Carbon Fiber", "Titanium", "Stainless Steel", "Composite"])
        self.setFixedFontSize(self.materialComboBox, 10)
        self.customizationLayout.addWidget(self.materialComboBox)

        self.customizationLayout.addWidget(QLabel('Number of Engines:'))
        self.engineCountSpinBox = QDoubleSpinBox()
        self.engineCountSpinBox.setRange(1, 30)
        self.engineCountSpinBox.setDecimals(0)
        self.setFixedFontSize(self.engineCountSpinBox, 10)
        self.customizationLayout.addWidget(self.engineCountSpinBox)

        self.customizationLayout.addWidget(QLabel('Primary Propellant:'))
        self.primaryPropellantComboBox = QComboBox()
        self.primaryPropellantList = [
            "Liquid Oxygen (LOX)", "Liquid Hydrogen (LH2)", "RP-1 (Hydrocarbon)", "Hypergolic Propellant (H2O2, N2O4)",
            "Solid Propellant", "Methane", "Hypergolic Propellant (N2O4 + Hydrazine)", "Hypergolic Propellant (N2O4 + UDMH)",
            "Solid Propellant (Aluminum + KClO4)", "Hypergolic Propellant (N2O4 + MMH)", "Solid Propellant (Al + NH4ClO4)",
            "Hypergolic Propellant (H2O2 + UDMH)", "Solid Propellant (Synthetic Rubber)", "Methane + Solid Propellant",
            "Liquid Hydrogen (LH2) + Solid Propellant", "Liquid Oxygen (LOX) + Solid Propellant",
            "Hypergolic Propellant (H2O2 + N2H4)", "Liquid Oxygen (LOX) + Ammonia", "RP-1 + Nitrogen Oxides",
            "Liquid Hydrogen (LH2) + Nitrogen Oxides", "Solid Propellant (Synthetic Rubber) + LOX", "Methane + RP-1",
            "Hypergolic Propellant (H2O2 + N2H4)", "Liquid Hydrogen (LH2) + N2O4", "RP-1 + Hypergolic Propellant (N2O4)",
            "Solid Propellant (Al + KClO4)", "Liquid Hydrogen (LH2)", "Methane + Liquid Oxygen (LOX)",
            "Hypergolic Propellant (N2O4 + MMH)", "Liquid Oxygen (LOX) + UDMH", "Hypergolic Propellant (H2O2 + MMH)",
            "Solid Propellant (Synthetic Rubber)", "RP-1 + Hypergolic Propellant (UDMH)",
            "Liquid Hydrogen (LH2) + Solid Propellant + LOX", "Hypergolic Propellant (N2O4 + Hydrazine)",
            "Solid Propellant (Al + NH4ClO4)", "Liquid Oxygen (LOX) + Nitrogen Oxides", "Hypergolic Propellant (N2O4 + UDMH)",
            "Methane + RP-1", "Liquid Hydrogen (LH2) + MMH", "Liquid Oxygen (LOX) + RP-1 + Nitrogen Oxides",
            "Liquid Hydrogen (LH2) + Solid Propellant", "Hypergolic Propellant (H2O2 + N2H4)",
            "Solid Propellant (KClO4 + Al)", "Liquid Hydrogen (LH2) + N2O4", "RP-1 + Nitrogen Oxides",
            "Liquid Oxygen (LOX) + Hypergolic Propellant (UDMH)", "Methane + Liquid Oxygen (LOX)",
            "Solid Propellant (Al + Fe2O3)", "Hypergolic Propellant (N2O4 + Hydrazine)", "Biofuel (e.g., Ethanol)",
            "Hydrogen Peroxide (H2O2) - Low Concentration", "Liquid Methane + Liquid Oxygen (LOX)",
            "Electric Propulsion (Ion Thrusters)", "Hall Effect Thrusters", "Gridded Ion Thrusters"
        ]
        self.primaryPropellantComboBox.addItems(self.primaryPropellantList)
        self.setFixedFontSize(self.primaryPropellantComboBox, 10)
        self.customizationLayout.addWidget(self.primaryPropellantComboBox)

        self.customizationLayout.addWidget(QLabel('Total Mass (kg):'))
        self.totalMassSpinBox = QDoubleSpinBox()
        self.totalMassSpinBox.setRange(1000, 100000)
        self.setFixedFontSize(self.totalMassSpinBox, 10)
        self.customizationLayout.addWidget(self.totalMassSpinBox)

        self.customizationLayout.addWidget(QLabel('Propulsion Stages:'))
        self.stageCountSpinBox = QSpinBox()
        self.stageCountSpinBox.setRange(1, 5)
        self.setFixedFontSize(self.stageCountSpinBox, 10)
        self.customizationLayout.addWidget(self.stageCountSpinBox)

        self.customizationWidget = QWidget()
        self.customizationWidget.setLayout(self.customizationLayout)
        self.customizationWidget.setVisible(False)

        self.customizationTankLayout = QVBoxLayout()
        self.customizationTankLayout.addWidget(self.customizationWidget)

        self.contentLayout = QVBoxLayout()
        self.contentLayout.addWidget(self.maxSpeedLabel)
        self.contentLayout.addWidget(self.maxSpeedSpinBox)
        self.contentLayout.addWidget(self.orbitLabel)
        self.contentLayout.addWidget(self.orbitSpinBox)
        self.contentLayout.addWidget(self.returnStatusLabel)
        self.contentLayout.addWidget(self.returnStatusComboBox)
        self.contentLayout.addWidget(self.launchDelayLabel)
        self.contentLayout.addWidget(self.launchDelaySpinBox)
        self.contentLayout.addWidget(self.launchDateLabel)
        self.contentLayout.addWidget(self.launchDateEdit)
        self.contentLayout.addWidget(self.launchAngleLabel)
        self.contentLayout.addWidget(self.launchAngleSpinBox)
        self.contentLayout.addWidget(self.rocketSelectionLabel)
        self.contentLayout.addWidget(self.rocketComboBox)
        self.contentLayout.addLayout(self.customizationTankLayout)

        self.mainLayout.addLayout(self.contentLayout)

        self.finalizeButton = QPushButton('Finalize Selection')
        self.finalizeButton.clicked.connect(self.finalizeSelection)
        self.setFixedFontSize(self.finalizeButton, 12)
        self.finalizeButton.setFixedSize(280, 40)
        self.mainLayout.addWidget(self.finalizeButton, alignment=Qt.AlignBottom)

        self.setLayout(self.mainLayout)

        self.subPropellantLabels = []
        self.subPropellantCombos = []

    def resetWidgets(self):
        self.maxSpeedSpinBox.setValue(1)
        self.orbitSpinBox.setValue(1)
        self.returnStatusComboBox.setCurrentIndex(0)
        self.launchDelaySpinBox.setValue(0)
        self.launchDateEdit.setDate(self.launchDateEdit.minimumDate())
        self.launchAngleSpinBox.setValue(0)
        self.rocketComboBox.setCurrentIndex(0)
        self.customizationWidget.setVisible(False)
        self.fuelTankCountSpinBox.setValue(1)
        self.rocketNameInput.clear()
        self.materialComboBox.setCurrentIndex(0)
        self.engineCountSpinBox.setValue(1)
        self.primaryPropellantComboBox.setCurrentIndex(0)
        self.totalMassSpinBox.setValue(1000)
        self.stageCountSpinBox.setValue(1)

        for label in self.subPropellantLabels:
            self.customizationLayout.removeWidget(label)
            label.deleteLater()
        for combo in self.subPropellantCombos:
            self.customizationLayout.removeWidget(combo)
            combo.deleteLater()
        self.subPropellantLabels.clear()
        self.subPropellantCombos.clear()

    def handleRocketSelection(self):
        selectedRocket = self.rocketComboBox.currentText()
        if selectedRocket == "Customize":
            self.customizationWidget.setVisible(True)
        else:
            self.customizationWidget.setVisible(False)

    def createPropellantWidgets(self):
        for label in self.subPropellantLabels:
            self.customizationLayout.removeWidget(label)
            label.deleteLater()
        for combo in self.subPropellantCombos:
            self.customizationLayout.removeWidget(combo)
            combo.deleteLater()
        self.subPropellantLabels.clear()
        self.subPropellantCombos.clear()

        num_tanks = self.fuelTankCountSpinBox.value()
        
        for i in range(num_tanks):
            subPropellantLabel = QLabel(f'Sub-Propellant {i + 1}:')
            self.setFixedFontSize(subPropellantLabel, 10)
            subPropellantComboBox = QComboBox()
            subPropellantComboBox.addItems(self.primaryPropellantList)
            self.setFixedFontSize(subPropellantComboBox, 10)
            self.subPropellantLabels.append(subPropellantLabel)
            self.subPropellantCombos.append(subPropellantComboBox)
            self.customizationLayout.addWidget(subPropellantLabel)
            self.customizationLayout.addWidget(subPropellantComboBox)

    def finalizeSelection(self):
        try:
            rocket_type = self.rocketComboBox.currentText()
            max_speed = self.maxSpeedSpinBox.value()
            orbit = self.orbitSpinBox.value()
            return_status = self.returnStatusComboBox.currentText()
            launch_delay = self.launchDelaySpinBox.value()
            launch_angle = self.launchAngleSpinBox.value()
            launch_date = self.launchDateEdit.date().toString(Qt.ISODate)

            content = (
                f"Selected Rocket Type: {rocket_type}\n"
                f"Max Speed: {max_speed} km/s\n"
                f"Orbit: {orbit} km\n"
                f"Return Status: {return_status}\n"
                f"Launch Delay: {launch_delay} minutes\n"
                f"Launch Date: {launch_date}\n"
                f"Launch Angle: {launch_angle}°\n"
            )

            if rocket_type == "Customize":
                rocket_name = self.rocketNameInput.text()
                material = self.materialComboBox.currentText()
                engine_count = self.engineCountSpinBox.value()
                primary_propellant = self.primaryPropellantComboBox.currentText()
                total_mass = self.totalMassSpinBox.value()
                stage_count = self.stageCountSpinBox.value()

                content += (
                    f"Rocket Name: {rocket_name}\n"
                    f"Material: {material}\n"
                    f"Number of Engines: {engine_count}\n"
                    f"Primary Propellant: {primary_propellant}\n"
                    f"Total Mass: {total_mass} kg\n"
                    f"Propulsion Stages: {stage_count}\n"
                )

                for i, combo in enumerate(self.subPropellantCombos):
                    content += f"Sub-Propellant {i + 1}: {combo.currentText()}\n"

            file_path = 'rocket_selection_details.txt'
            with open(file_path, 'w') as file:
                file.write(content)

            QMessageBox.information(self, 'Info', f'Selection finalized and saved to {file_path}')

        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, 'Error', f"An error occurred: {e}")

    def setFixedFontSize(self, widget, size):
        font = widget.font()
        font.setPointSize(size)
        widget.setFont(font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RocketSelector()
    app.setStyle('Fusion')
    ex.show()
    sys.exit(app.exec_())
