# Copyright (c) 2017 Thomas Karl Pietrowski

# TODOs:
# * Adding selection to separately import parts from an assembly

# Uranium/Cura
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("CuraSolidWorksIntegrationPlugin")
from UM.Logger import Logger

# Our plugin
from .CommonComReader import CommonCOMReader
from .SolidWorksConstants import SolidWorksEnums

class SolidWorksReader(CommonCOMReader):
    
    def __init__(self):
        self._extension_part = ".SLDPRT"
        self._extension_assembly = ".SLDASM"
        self._supported_extensions = [self._extension_part.lower(),
                                      self._extension_assembly.lower(),
                                      ]

        super(SolidWorksReader, self).__init__("SldWorks.Application", "SolidWorks")
        
        self._convertAssemblyIntoOnce = True # False is not implemented now!
        
        self._revision = None
        self._revision_major = None
        self._revision_minor = None
        self._revision_patch = None

    def setAppVisible(self, state):
        self._app_instance.Visible = state
    
    def getAppVisible(self, state):
        return self._app_instance.Visible
    
    def startApp(self, visible=False):
        CommonCOMReader.startApp(self, visible=visible)
        
        # Getting revision after starting
        self._revision = [int(x) for x in self._app_instance.RevisionNumber.split(".")]
        self._revision_major = self._revision[0]
        self._revision_minor = self._revision[1]
        self._revision_patch = self._revision[2]
        
        # Re-generate a list of preferred file formats
        self.updateFormatsFirstChoise()
    
    def updateFormatsFirstChoise(self):
        self._fileFormatsFirstChoise = ["stl"]
        if self._revision_major >= 25 and "3mf" in self._readerForFileformat.keys():
            self._fileFormatsFirstChoise.insert(0, "3mf")

        return self._fileFormatsFirstChoise
    
    def checkApp(self):
        functionsToBeChecked = ("OpenDoc", "CloseDoc")
        for function in functionsToBeChecked:
            try:
                getattr(self._app_instance, function)
            except:
                Logger.logException("e", "Error which occured when checking for a valid app instance")
                return False
        return True
    
    def closeApp(self):
        self._app_instance.ExitApp()
        del(self._app_instance)        
        self._app_instance = None

    def walkComponentsInAssembly(self, root = None):
        if root == None:
            root = self.rootComponent
        
        children = root.GetChildren
        
        if children:
            children = [self.walkComponentsInAssembly(child) for child in children]
            return (root, children)
        else:
            return root
        
        """
        models = self.model.GetComponents(True)
        
        for model in models:
            #Logger.log("d", model.GetModelDoc2())
            #Logger.log("d", repr(model.GetTitle))
            Logger.log("d", repr(model.GetPathName))
            #Logger.log("d", repr(model.GetType))
            if model.GetPathName in ComponentsCount.keys():
                ComponentsCount[model.GetPathName] = ComponentsCount[model.GetPathName] + 1
            else:
                ComponentsCount[model.GetPathName] = 1

        for key in ComponentsCount.keys():
            Logger.log("d", "Found %s %s-times in the assembly!" %(key, ComponentsCount[key]))
        """

    def openForeignFile(self, **kwargs):
        if kwargs["foreignFormat"].upper() == self._extension_part:
            filetype = SolidWorksEnums.FileTypes.SWpart
        elif kwargs["foreignFormat"].upper() == self._extension_assembly:
            filetype = SolidWorksEnums.FileTypes.SWassembly
        else:
            raise NotImplementedError("Unknown extension. Something went terribly wrong!")

        self.model = self._app_instance.OpenDoc(kwargs["foreignFile"], filetype)
        self.configuration = self.model.getActiveConfiguration
        self.rootComponent = self.configuration.GetRootComponent

        if filetype == SolidWorksEnums.FileTypes.SWassembly:
            Logger.log("d", 'walkComponentsInAssembly: ' + repr(self.walkComponentsInAssembly()))

    def exportFileAs(self, **kwargs):
        if kwargs["tempType"] == "stl":
            if kwargs["foreignFormat"].upper() == self._extension_assembly:
                # Backing up current setting of swSTLComponentsIntoOneFile
                swSTLComponentsIntoOneFileBackup = self._app_instance.GetUserPreferenceToggle(SolidWorksEnums.UserPreferences.swSTLComponentsIntoOneFile)
                self._app_instance.SetUserPreferenceToggle(SolidWorksEnums.UserPreferences.swSTLComponentsIntoOneFile, self._convertAssemblyIntoOnce)

            swExportSTLQualityBackup = self._app_instance.GetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportSTLQuality)
            self._app_instance.SetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportSTLQuality, SolidWorksEnums.swSTLQuality_e.swSTLQuality_Fine)
            
            # Changing the default unit for STLs to mm, which is expected by Cura
            swExportStlUnitsBackup = self._app_instance.GetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportStlUnits)
            self._app_instance.SetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportStlUnits, SolidWorksEnums.swLengthUnit_e.swMM)
            
            # Changing the output type temporary to binary
            swSTLBinaryFormatBackup = self._app_instance.GetUserPreferenceToggle(SolidWorksEnums.swUserPreferenceToggle_e.swSTLBinaryFormat)
            self._app_instance.SetUserPreferenceToggle(SolidWorksEnums.swUserPreferenceToggle_e.swSTLBinaryFormat, True)
        
        self.model.SaveAs(kwargs["tempFile"])
        
        if kwargs["tempType"] == "stl":
            # Restoring swSTLBinaryFormat
            self._app_instance.SetUserPreferenceToggle(SolidWorksEnums.swUserPreferenceToggle_e.swSTLBinaryFormat, swSTLBinaryFormatBackup)
            
            # Restoring swExportStlUnits
            self._app_instance.SetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportStlUnits, swExportStlUnitsBackup)
            
            # Restoring swSTLQuality_Fine
            self._app_instance.SetUserPreferenceIntegerValue(SolidWorksEnums.swUserPreferenceIntegerValue_e.swExportSTLQuality, swExportSTLQualityBackup)
            
            if kwargs["foreignFormat"].upper() == self._extension_assembly:
                # Restoring swSTLComponentsIntoOneFile
                self._app_instance.SetUserPreferenceToggle(SolidWorksEnums.UserPreferences.swSTLComponentsIntoOneFile, swSTLComponentsIntoOneFileBackup)
    
    def closeForeignFile(self, **kwargs):
        self._app_instance.CloseDoc(kwargs["foreignFile"])
    
    def areReadersAvailable(self):
        return bool(self._readerForFileformat)

    ## Decide if we need to use ascii or binary in order to read file
