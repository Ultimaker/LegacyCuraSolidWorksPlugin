// Copyright (c) 2017 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import UM 1.2 as UM

UM.Dialog
{
    width: 300 * Screen.devicePixelRatio;
    minimumWidth: 300 * Screen.devicePixelRatio;

    height: 100 * Screen.devicePixelRatio;
    minimumHeight: 100 * Screen.devicePixelRatio;

    title: catalog.i18nc("@title:window", "Import SolidWorks File as STL...")

    onVisibilityChanged:
    {
        if (visible)
        {
            qualityDropdown.currentIndex = 1;
        }
    }

    GridLayout
    {
        UM.I18nCatalog{id: catalog; name: "cura"}
        anchors.fill: parent;
        Layout.fillWidth: true
        columnSpacing: 16
        rowSpacing: 4
        columns: 1

        UM.TooltipArea {
            Layout.fillWidth:true
            height: childrenRect.height
            text: catalog.i18nc("@info:tooltip", "Quality of the Exported STL")
            Row {
                width: parent.width

                Label {
                    text: catalog.i18nc("@action:label", "STL Quality")
                    width: 50
                    anchors.verticalCenter: parent.verticalCenter
                }

                ComboBox
                {
                    id: qualityDropdown
                    model: ["Coarse", "Fine"]
                    currentIndex: 1
                }
            }
        }
    }

    rightButtons: [
        Button
        {
            id: ok_button
            text: catalog.i18nc("@action:button", "OK")
            onClicked:
            {
                manager.setQuality(qualityDropdown.currentText);
                manager.onOkButtonClicked();
            }
            enabled: true
        },
        Button
        {
            id: cancel_button
            text: catalog.i18nc("@action:button", "Cancel")
            onClicked: { manager.onCancelButtonClicked() }
            enabled: true
        }
    ]
}
