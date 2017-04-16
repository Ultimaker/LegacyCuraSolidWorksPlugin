# Copyright (c) 2017 Thomas Karl Pietrowski

# Buildins
import os
import tempfile

# Uranium/Cura
from UM.Application import Application
from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("CuraSolidWorksIntegrationPlugin")
from UM.Message import Message
from UM.Logger import Logger
from UM.Mesh.MeshReader import MeshReader
from UM.PluginRegistry import PluginRegistry
from UM.Scene.SceneNode import SceneNode

# PyWin32
import win32com.client
import pythoncom
import pywintypes

class CommonCOMReader(MeshReader):    
    def __init__(self, app_name, app_friendlyName):
        self._app_name = app_name
        self._app_friendlyName = app_friendlyName
        
        # Start/stop behaviour
        
        # Technically neither preloading nor keeping the instance up, is possible, since Cura calls the file reader from different/new threads
        # The error when trying to use it here is:
        # > pywintypes.com_error: (-2147417842, 'The application called an interface that was marshalled for a different thread.', None, None)
        self._app_preload = False
        self._app_keep_running = False
        
        """
        if self._app_preload and not self._app_keep_running:
            self._app_keep_running = True
        """
        
        # Preparations
        """
        if self._app_preload:
            Logger.log("d", "Preloading %s..." %(self._app_friendlyName))
            self.startApp()
        """
        
        Logger.log("d", "Looking for readers...")
        self.__init_builtin_readers__()
    
    def __init_builtin_readers__(self):
        self._fileFormatsFirstChoise = [] # Ordered list of preferred formats
        self._readerForFileformat = {}
        
        # Trying 3MF first because it describes the model much better..
        # However, this is untested since this plugin was only tested with STL support
        if PluginRegistry.getInstance().isActivePlugin("3MFReader"):
            self._readerForFileformat["3mf"] = PluginRegistry.getInstance().getPluginObject("3MFReader")
            self._fileFormatsFirstChoise.append("3mf")

        if PluginRegistry.getInstance().isActivePlugin("STLReader"):
            self._readerForFileformat["stl"] = PluginRegistry.getInstance().getPluginObject("STLReader")
            self._fileFormatsFirstChoise.append("stl")
            
        if not len(self._readerForFileformat):
            Logger.log("d", "Could not find any reader for (probably) supported file formats!")
    
    def getSaveTempfileName(self, suffix = "" ):
        # Only get a save name for a temp_file here...
        temp_stl_file = tempfile.NamedTemporaryFile()
        temp_stl_file_name = "%s%s" %(temp_stl_file.name, suffix)
        temp_stl_file.close()
        
        return temp_stl_file_name
    
    def startApp(self, visible = False ):
        Logger.log("d", "Starting %s..." %(self._app_friendlyName))
        app_instance = win32com.client.Dispatch(self._app_name)
        
        self.setAppVisible(visible, app_instance = app_instance)
        
        return app_instance
    
    def checkApp(self):
        raise NotImplementedError("Checking app is not implemented!")
    
    def getAppVisible(self, state):
        raise NotImplementedError("Toggle for visibility not implemented!")
    
    def setAppVisible(self, state, **options):
        raise NotImplementedError("Toggle for visibility not implemented!")
    
    def closeApp(self, **options):
        raise NotImplementedError("Procedure how to close your app is not implemented!")
    
    def openForeignFile(self, **options):
        "This function shall return options again. It optionally contains other data, which is needed by the reader for other tasks later."
        raise NotImplementedError("Opening files is not implemented!")
    
    def exportFileAs(self, model, **options):
        raise NotImplementedError("Exporting files is not implemented!")
    
    def closeForeignFile(self, **options):
        raise NotImplementedError("Closing files is not implemented!")
    
    def nodePostProcessing(self, node):
        return node
    
    def read(self, filePath):
        options = {"foreignFile" : filePath,
                   "foreignFormat" : os.path.splitext(filePath)[1],
                  }
        
        # Making our COM connection thread-safe accross the whole plugin
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        # Starting app, if needed
        try:
            options["app_instance"] = self.startApp()
        except pywintypes.com_error:
            Logger.logException("e", "Error while starting %s. Maybe the guest application can't verify it's licence, etc.." %(self._app_name))
            error_message = Message(i18n_catalog.i18nc("@info:status", "Error while opening %s. Check whether %s works normally!" %(self._app_friendlyName, self._app_friendlyName)))
            error_message.show()
            return None
        except Exception:
            Logger.logException("e", "Failed to start <%s>..." %(self._app_name))
            error_message = Message(i18n_catalog.i18nc("@info:status", "Error while starting %s!" %(self._app_friendlyName)))
            error_message.show()
            return None
        
        # Tell the 3rd party application to open a file...
        Logger.log("d", "Opening file with %s..."  %(self._app_friendlyName))
        options = self.openForeignFile(**options)

        # Append all formats which are not preferred to the end of the list
        fileFormats = self._fileFormatsFirstChoise
        for fileFormat in self._readerForFileformat.keys():
            if fileFormat not in fileFormats:
                fileFormats.append(fileFormat)

        # Trying to convert into all formats 1 by 1 and continue with the successful export
        Logger.log("i", "Trying to convert into: %s" %(fileFormats))
        for fileFormat in fileFormats:
            Logger.log("d", "Trying to convert <%s> into  '%s'" %(filePath, fileFormat))
            
            options["tempType"] = fileFormat
            
            options["tempFile"] = self.getSaveTempfileName(".%s" %(fileFormat.upper()))
            Logger.log("d", "Using temporary file <%s>" %(options["tempFile"]))

            # In case there is already a file with this name (very unlikely...)
            if os.path.isfile(options["tempFile"]):
                Logger.log("w", "Removing already available file, called: %s" %(options["tempFile"]))
                os.remove(options["tempFile"])

            Logger.log("d", "Saving as: <%s>" %(options["tempFile"]))
            try:
                self.exportFileAs(**options)
            except:
                Logger.logException("e", "Could not export <%s> into '%s'." %(filePath, fileFormat))
                continue

            if os.path.isfile(options["tempFile"]):
                Logger.log("d", "Saved as: <%s>" %(options["tempFile"]))
            else:
                Logger.log("d", "Temporary file not found after export!")
                continue

            # Opening the resulting file in Cura
            try:
                #reader = self._readerForFileformat[fileFormat]
                reader = Application.getInstance().getMeshFileHandler().getReaderForFile(options["tempFile"])
                if not reader:
                    Logger.log("d", "Found no reader for %s. That's strange...")
                    continue
                Logger.log("d", "Using reader: %s" %(reader.getPluginId()))
                temp_scene_node = reader.read(options["tempFile"])
            except:
                Logger.logException("e", "Failed to open exported <%s> file in Cura!" %(fileFormat))
                continue

            # Remove the temp_file again
            Logger.log("d", "Removing temporary STL file, called <%s>", options["tempFile"])
            os.remove(options["tempFile"])

            break

        # Closing document in the app
        self.closeForeignFile(**options)
        
        # Closing the app again..
        self.closeApp(**options)
        
        # Turning off thread-safity again...
        pythoncom.CoUninitialize()

        scene_node = SceneNode()
        temp_scene_node = self.nodePostProcessing(temp_scene_node)
        mesh = temp_scene_node.getMeshDataTransformed()
        
        # When using 3MF as the format to convert into we get an list of meshes instead of only one mesh directly.
        # This is a little workaround since reloading of 3MF files doesn't work at the moment.
        if type(mesh) == list:
            error_message = Message(i18n_catalog.i18nc("@info:status", "Please keep in mind, that you have to reopen your SolidWorks file manually! Reloading the model won't work!"))
            error_message.show()
            mesh = mesh.set(file_name=None)
        else:
            mesh = mesh.set(file_name=filePath)
        scene_node.setMeshData(mesh)

        if scene_node:
            return scene_node
        return