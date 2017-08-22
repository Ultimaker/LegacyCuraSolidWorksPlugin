// Copyright (c) 2017 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtQuick.Window 2.1

import UM 1.2 as UM
import Cura 1.0 as Cura

UM.Dialog
{
    id: base
    width: 1250 * Screen.devicePixelRatio
    minimumWidth: 1250 * Screen.devicePixelRatio

    height: 650 * Screen.devicePixelRatio
    minimumHeight: 650 * Screen.devicePixelRatio

    title: catalog.i18nc("@title:window", "How to install Cura SolidWorks macro")

    property var currentStepIndex: 0

    onVisibilityChanged:
    {
        setCurrentStepIndex(0);
    }

    function setCurrentStepIndex(index)
    {
        currentStepIndex = index;
        for (var i = 0; i < stepModel.count; ++i)
        {
            const activated = i == currentStepIndex;
            stepModel.get(i).activated = activated;
            animation.source = "macro/tutorial/" + String(currentStepIndex + 1) + ".gif";
            animationSlider.maximumValue = animation.frameCount;
            animationSlider.value = animation.currentFrame;
        }
    }

    Row
    {
        spacing: 6 * Screen.devicePixelRatio

        UM.I18nCatalog { id: catalog; name: "cura" }

        Column
        {
            id: stepsColumn
            anchors.margins: UM.Theme.getSize("default_margin").width
            width: 200 * Screen.devicePixelRatio

            spacing: 6 * Screen.devicePixelRatio

            Label
            {
                anchors.margins: UM.Theme.getSize("default_margin").width

                text: catalog.i18nc("@description:label", "Steps:")
                wrapMode: Text.WordWrap
                font.pointSize: 14
                font.bold: true
            }

            ListModel
            {
                id: stepModel

                ListElement {
                    text: "Start SolidWorks"
                    description: "Start SolidWorks 2016/2017 and make sure that you have a document open."
                    activated: false
                }
                ListElement {
                    text: "Open 'Customize' Dialog"
                    description: "Select 'Customize' on the menu bar and open the 'Customize' dialog."
                    activated: false
                }
                ListElement {
                    text: "Switch to 'Macro'"
                    description: "- Switch to 'Commands'\n- Choose 'Macro'"
                    activated: false
                }
                ListElement {
                    text: "Add New Macro Button"
                    description: "- Trag and drop the 'New Macro Button' icon onto the toolbar\n- Provide the Macro file location and an icon for it"
                    activated: false
                }
                ListElement {
                    text: "Done!"
                    description: "- Now you have your 'Export model to Cura' button!"
                    activated: false
                }
            }

            Repeater
            {
                model: stepModel

                Label
                {
                    anchors.margins: UM.Theme.getSize("default_margin").width

                    text: String(model.index + 1) + ". " + catalog.i18nc("@title:label", model.text)
                    wrapMode: Text.WordWrap
                    font.bold: model.activated

                    MouseArea
                    {
                        anchors.fill: parent
                        onClicked:
                        {
                            base.setCurrentStepIndex(model.index);
                        }
                    }
                }
            }

            Path
            {
                PathLine {}
            }

            Button
            {
                id: getMacroAndIconLocationButton
                anchors.topMargin: UM.Theme.getSize("default_margin").width * 10
                anchors.leftMargin: UM.Theme.getSize("default_margin").width
                anchors.rightMargin: UM.Theme.getSize("default_margin").width
                anchors.bottomMargin: UM.Theme.getSize("default_margin").width
                width: 180
                height: 40
                text: catalog.i18nc("@action:button", "Open the directory\nwith macro and icon")
                onClicked:
                {
                    manager.openMacroAndIconDirectory();
                }
            }
        }

        Column
        {
            id: infoColumn
            anchors.margins: UM.Theme.getSize("default_margin").width
            width: base.width - stepsColumn - 20 * Screen.devicePixelRatio

            spacing: 8 * Screen.devicePixelRatio

            Label
            {
                anchors.margins: UM.Theme.getSize("default_margin").width

                text: catalog.i18nc("@description:label", "Instructions:")
                wrapMode: Text.WordWrap
                font.pointSize: 14
                font.bold: true
            }

            Label
            {
                id: tutorialText

                anchors.margins: UM.Theme.getSize("default_margin").width

                text: catalog.i18nc("@description:label", stepModel.get(currentStepIndex).description)
                wrapMode: Text.WordWrap
                font.pointSize: 12
            }

            AnimatedImage
            {
                id: animation
                anchors.margins: UM.Theme.getSize("default_margin").width
                width: 1000 * Screen.devicePixelRatio
                height: 500 * Screen.devicePixelRatio
                source: "macro/tutorial/" + String(currentStepIndex + 1) + ".gif"

                onSourceChanged:
                {
                    animationSlider.maximumValue = frameCount;
                    animationSlider.value = currentFrame;
                }
            }

            Row
            {
                spacing: 10 * Screen.devicePixelRatio

                Button
                {
                    id: playPauseButton
                    text:
                    {
                        if (!animation.playing)
                        {
                            return catalog.i18nc("@action:playpause", "Play");
                        }
                        else
                        {
                            return catalog.i18nc("@action:playpause", "Pause");
                        }
                    }

                    onClicked:
                    {
                        var previousFrame = animation.currentFrame;
                        const wasPaused = !animation.playing;
                        animation.playing = !animation.playing;
                        if (wasPaused)
                        {
                            animation.currentFrame = previousFrame;
                        }
                    }
                }

                Slider
                {
                    id: animationSlider
                    anchors.margins: UM.Theme.getSize("default_margin").width
                    width: 500 * Screen.devicePixelRatio
                    orientation: Qt.Horizontal
                    stepSize: 1
                    minimumValue: 0
                    value: animation.currentFrame

                    property var wasPlaying: true

                    onValueChanged:
                    {
                        wasPlaying = animation.playing;
                        animation.currentFrame = value;
                        animation.playing = wasPlaying;
                    }

                    onPressedChanged:
                    {
                        if (pressed)
                        {
                            wasPlaying = animation.playing;
                            animation.playing = false;
                        }
                        animation.playing = wasPlaying;
                    }
                }

                Binding
                {
                    target: animationSlider
                    property: "value"
                    value: animation.currentFrame
                }
            }
        }
    }


    rightButtons: [
        Button
        {
            id: prevStepButton
            anchors.margins: UM.Theme.getSize("default_margin").width
            text: catalog.i18nc("@action:button", "Previous Step")
            enabled: base.currentStepIndex > 0
            onClicked:
            {
                base.setCurrentStepIndex(base.currentStepIndex - 1);
            }
        },
        Button
        {
            id: nextStepButton
            anchors.margins: UM.Theme.getSize("default_margin").width
            text:
            {
                if (base.currentStepIndex + 1 == stepModel.count)
                {
                    return catalog.i18nc("@action:button", "Done")
                }
                else
                {
                    return catalog.i18nc("@action:button", "Next Step")
                }
            }
            onClicked:
            {
                if (base.currentStepIndex + 1 == stepModel.count)
                {
                    close();
                }
                else
                {
                    base.setCurrentStepIndex(base.currentStepIndex + 1);
                }
            }
        },
        Button
        {
            id: closeButton
            anchors.margins: UM.Theme.getSize("default_margin").width
            text: catalog.i18nc("@action:button", "Close")
            onClicked:
            {
                close();
            }
            enabled: true
        }
    ]
}
