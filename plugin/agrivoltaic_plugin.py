from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox
)
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsRasterShader,
    QgsColorRampShader, QgsSingleBandPseudoColorRenderer,
    QgsRasterRange
)
from qgis.PyQt.QtGui import QColor
import processing


class AgrivoltaicOptimizer(QDockWidget):

    def __init__(self, iface):
        super().__init__("Agrivoltaic Optimizer")
        self.iface = iface

        container = QWidget()
        layout = QVBoxLayout()

        # ── GHI Slider ──────────────────────────────────
        self.label_ghi = QLabel("Min GHI Threshold: 5 kWh/m2/day")
        layout.addWidget(self.label_ghi)
        self.slider_ghi = QSlider(Qt.Horizontal)
        self.slider_ghi.setMinimum(0)
        self.slider_ghi.setMaximum(10)
        self.slider_ghi.setValue(5)
        self.slider_ghi.valueChanged.connect(self.update_ghi)
        layout.addWidget(self.slider_ghi)

        # ── Slope Slider ─────────────────────────────────
        self.label_slope = QLabel("Max Slope Tolerance: 10 degrees")
        layout.addWidget(self.label_slope)
        self.slider_slope = QSlider(Qt.Horizontal)
        self.slider_slope.setMinimum(0)
        self.slider_slope.setMaximum(30)
        self.slider_slope.setValue(10)
        self.slider_slope.valueChanged.connect(self.update_slope)
        layout.addWidget(self.slider_slope)

        # ── Grid Slider ───────────────────────────────────
        self.label_grid = QLabel("Max Distance to Grid: 20 km")
        layout.addWidget(self.label_grid)
        self.slider_grid = QSlider(Qt.Horizontal)
        self.slider_grid.setMinimum(0)
        self.slider_grid.setMaximum(100)
        self.slider_grid.setValue(20)
        self.slider_grid.valueChanged.connect(self.update_grid)
        layout.addWidget(self.slider_grid)

        # ── Mode Selector ─────────────────────────────────
        self.label_mode = QLabel("Filter Mode:")
        layout.addWidget(self.label_mode)
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            "All Classes (1-5)",
            "Moderate + High + Prime (3-5)",
            "High + Prime Only (4-5)",
            "Prime Only (5)"
        ])
        layout.addWidget(self.combo_mode)

        # ── Execute Button ────────────────────────────────
        self.btn_execute = QPushButton("Execute MCDA")
        self.btn_execute.clicked.connect(self.execute_mcda)
        self.btn_execute.setStyleSheet(
            "QPushButton { background-color: #2e7d32; color: white; "
            "font-weight: bold; padding: 6px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #43a047; }"
        )
        layout.addWidget(self.btn_execute)

        # ── Status Label ──────────────────────────────────
        self.label_status = QLabel("Status: Ready")
        self.label_status.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.label_status)

        layout.addStretch()
        container.setLayout(layout)
        self.setWidget(container)

    # ── Slider Update Methods ─────────────────────────────

    def update_ghi(self):
        self.label_ghi.setText(
            "Min GHI Threshold: " + str(self.slider_ghi.value()) + " kWh/m2/day"
        )

    def update_slope(self):
        self.label_slope.setText(
            "Max Slope Tolerance: " + str(self.slider_slope.value()) + " degrees"
        )

    def update_grid(self):
        self.label_grid.setText(
            "Max Distance to Grid: " + str(self.slider_grid.value()) + " km"
        )

    # ── Symbology Helper ──────────────────────────────────

    def apply_symbology(self, layer, classes):
        """
        classes = list of (value, QColor, label)
        Applies exact-match pseudocolor renderer to given layer.
        """
        shader     = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampType(QgsColorRampShader.Type.Exact)

        items = [
            QgsColorRampShader.ColorRampItem(v, c, lbl)
            for v, c, lbl in classes
        ]
        color_ramp.setColorRampItemList(items)
        shader.setRasterShaderFunction(color_ramp)

        renderer = QgsSingleBandPseudoColorRenderer(
            layer.dataProvider(), 1, shader
        )
        layer.setRenderer(renderer)

        # Force value 0 → fully transparent
        transp_list = [QgsRasterRange(0.0, 0.0)]
        layer.dataProvider().setUserNoDataValue(1, transp_list)

        layer.triggerRepaint()

    # ── Main MCDA Execution ───────────────────────────────

    def execute_mcda(self):
        print("\n" + "=" * 50)
        print("AGRIVOLTAIC MCDA RUNNING")
        print("=" * 50)

        ghi   = self.slider_ghi.value()
        slope = self.slider_slope.value()
        grid  = self.slider_grid.value()
        mode  = self.combo_mode.currentIndex()

        print("GHI Threshold  :", ghi)
        print("Slope Max      :", slope)
        print("Grid Max (km)  :", grid)
        print("Filter Mode    :", self.combo_mode.currentText())

        self.label_status.setText("Status: Running...")

        # ── Step 1: Find suitability layer ───────────────
        suit_layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if 'agrivoltaic_suitability' in lyr.name().lower():
                suit_layer = lyr
                break

        if not suit_layer:
            print("ERROR: agrivoltaic_suitability layer not found")
            self.label_status.setText("Status: ERROR — suitability layer missing")
            return

        # ── Step 2: Find grid distance layer ─────────────
        # Expects a raster named 'grid_distance' storing
        # distance-to-grid values in kilometres
        grid_layer = None
        for lyr in QgsProject.instance().mapLayers().values():
            if 'grid_distance' in lyr.name().lower() or \
               'grid_dist'     in lyr.name().lower() or \
               'distance_grid' in lyr.name().lower():
                grid_layer = lyr
                break

        if not grid_layer:
            print("WARNING: grid_distance layer not found")
            print("Grid filter will be SKIPPED")
            print("To enable it, load a raster named 'grid_distance'")
            print("containing distance-to-grid values in kilometres")
            self.label_status.setText("Status: WARNING — grid layer missing, skipped")
        else:
            print("Grid layer found:", grid_layer.name())

        # ── Step 3: Determine class filter ───────────────
        if mode == 0:
            min_class = 1
            label = "ALL"
        elif mode == 1:
            min_class = 3
            label = "MOD_HIGH_PRIME"
        elif mode == 2:
            min_class = 4
            label = "HIGH_PRIME"
        else:
            min_class = 5
            label = "PRIME_ONLY"

        # ── Step 4: Build raster calculator expression ───
        s = suit_layer.name()

        # Base suitability filter
        expression = (
            "( \"{s}@1\" >= {min_class} ) * \"{s}@1\""
        ).format(s=s, min_class=min_class)

        # Add GHI influence — boost expression only keeps
        # pixels where suitability >= min_class AND
        # the raw suitability score is above GHI-derived threshold
        ghi_class = max(1, min(5, round(ghi / 2)))
        expression = (
            "( \"{s}@1\" >= {min_class} AND \"{s}@1\" >= {ghi_class} ) "
            "* \"{s}@1\""
        ).format(s=s, min_class=min_class, ghi_class=ghi_class)

        # Add slope filter — high slope tolerance keeps more pixels
        # slope > 20 = strict (only flat land = high class)
        # slope <= 20 = relaxed
        if slope <= 10:
            slope_min = min_class + 1
        elif slope <= 20:
            slope_min = min_class
        else:
            slope_min = max(1, min_class - 1)

        expression = (
            "( \"{s}@1\" >= {slope_min} AND \"{s}@1\" >= {ghi_class} ) "
            "* \"{s}@1\""
        ).format(s=s, slope_min=slope_min, ghi_class=ghi_class)

        # Add grid distance filter if layer exists
        if grid_layer:
            g = grid_layer.name()
            expression = (
                "( \"{s}@1\" >= {slope_min} "
                "AND \"{s}@1\" >= {ghi_class} "
                "AND \"{g}@1\" <= {grid} ) "
                "* \"{s}@1\""
            ).format(
                s=s, g=g,
                slope_min=slope_min,
                ghi_class=ghi_class,
                grid=grid
            )

        print("\nExpression:", expression)

        # ── Step 5: Run raster calculator ────────────────
        layers_input = [suit_layer]
        if grid_layer:
            layers_input.append(grid_layer)

        try:
            result = processing.run("qgis:rastercalculator", {
                'EXPRESSION': expression,
                'LAYERS'    : layers_input,
                'OUTPUT'    : 'TEMPORARY_OUTPUT'
            })
        except Exception as e:
            print("ERROR in raster calculator:", str(e))
            self.label_status.setText("Status: ERROR — raster calculator failed")
            return

        # ── Step 6: Load filtered layer ──────────────────
        layer_name = (
            "Filtered_" + label +
            "_GHI"   + str(ghi) +
            "_Slope" + str(slope) +
            "_Grid"  + str(grid)
        )
        filtered = QgsRasterLayer(result['OUTPUT'], layer_name)

        if not filtered.isValid():
            print("ERROR: Filtered layer is not valid")
            self.label_status.setText("Status: ERROR — output layer invalid")
            return

        QgsProject.instance().addMapLayer(filtered)
        print("Filtered layer added:", layer_name)

        # ── Step 7: Apply full 5-class symbology ─────────
        self.apply_symbology(filtered, [
            (1, QColor(215, 25,  28),  "Unsuitable"),
            (2, QColor(253, 174, 97),  "Low Suitable"),
            (3, QColor(255, 255, 191), "Moderate Suitable"),
            (4, QColor(166, 217, 106), "High Suitable"),
            (5, QColor(26,  150, 65),  "Prime Agrivoltaic"),
        ])

        self.iface.mapCanvas().refresh()

        print("Symbology applied successfully")
        print("=" * 50)
        self.label_status.setText(
            "Status: Done — " + layer_name
        )


# ── Launch Function ───────────────────────────────────────

def launch_panel(iface):
    if hasattr(iface, "agrivoltaic_panel"):
        try:
            iface.agrivoltaic_panel.close()
        except Exception:
            pass

    iface.agrivoltaic_panel = AgrivoltaicOptimizer(iface)
    iface.addDockWidget(Qt.RightDockWidgetArea, iface.agrivoltaic_panel)
    iface.agrivoltaic_panel.show()
    print("Agrivoltaic Optimizer panel launched successfully")