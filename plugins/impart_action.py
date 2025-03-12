import pcbnew
import os.path
from pathlib import Path
import wx
from time import sleep
from threading import Thread
import sys
import traceback
import subprocess
import os
import venv

try:
    if __name__ == "__main__":
        from impart_gui import impartGUI
        from KiCadImport import import_lib
        from impart_helper_func import filehandler, config_handler, KiCad_Settings
        from impart_migration import find_old_lib_files, convert_lib_list
    else:
        # relative import is required in kicad
        from .impart_gui import impartGUI
        from .KiCadImport import import_lib
        from .impart_helper_func import filehandler, config_handler, KiCad_Settings
        from .impart_migration import find_old_lib_files, convert_lib_list
except Exception as e:
    print(traceback.format_exc())


def activate_virtualenv(venv_dir):
    """Activates a virtual environment, but creates it first if it does not exist."""
    venv_dir = os.path.abspath(venv_dir)

    if os.name == "nt":  # Windows
        if not os.path.exists(venv_dir):
            # venv.create(venv_dir, with_pip=True) # dont work
            kicad_executable = sys.executable
            kicad_bin_dir = os.path.dirname(kicad_executable)
            python_executable = os.path.join(kicad_bin_dir, "python.exe")
            subprocess.run(
                [python_executable, "-m", "venv", venv_dir],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            print(f"Virtual environment not found. Create new in {venv_dir} ...")

        python_executable = os.path.join(venv_dir, "Scripts", "python.exe")
        site_packages = os.path.join(venv_dir, "Lib", "site-packages")
    else:  # Linux / macOS
        if not os.path.exists(venv_dir):
            venv.create(venv_dir, with_pip=True)
            print(f"Virtual environment not found. Create new in {venv_dir} ...")
        python_executable = os.path.join(venv_dir, "bin", "python")
        site_packages = os.path.join(
            venv_dir,
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        )

    sys.path.insert(0, site_packages)
    return python_executable


def ensure_package(package_name, python_executable="python"):
    try:
        __import__(package_name)
        return True
    except ModuleNotFoundError:
        try:
            cmd = [python_executable, "-m", "pip", "install", package_name]
            print(" ".join(cmd))
            subprocess.check_call(cmd)
            __import__(package_name)
            return True
        except:
            return False


EVT_UPDATE_ID = wx.NewIdRef()


def EVT_UPDATE(win, func):
    win.Connect(-1, -1, EVT_UPDATE_ID, func)


class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_UPDATE_ID)
        self.data = data


class PluginThread(Thread):
    def __init__(self, wxObject):
        Thread.__init__(self)
        self.wxObject = wxObject
        self.stopThread = False
        self.start()

    def run(self):
        lenStr = 0
        global backend_h
        while not self.stopThread:
            if lenStr != len(backend_h.print_buffer):
                self.report(backend_h.print_buffer)
                lenStr = len(backend_h.print_buffer)
            sleep(0.5)

    def report(self, status):
        wx.PostEvent(self.wxObject, ResultEvent(status))


class impart_backend:

    def __init__(self):
        path2config = os.path.join(os.path.dirname(__file__), "config.ini")
        self.config = config_handler(path2config)
        path_seting = pcbnew.SETTINGS_MANAGER().GetUserSettingsPath()
        self.KiCad_Settings = KiCad_Settings(path_seting)
        self.runThread = False
        self.autoImport = False
        self.overwriteImport = False
        self.import_old_format = False
        self.localLib = False
        self.autoLib = False
        self.folderhandler = filehandler(".")
        self.print_buffer = ""
        self.importer = import_lib()
        self.importer.print = self.print2buffer

        def version_to_tuple(version_str):
            try:
                return tuple(map(int, version_str.split("-")[0].split(".")))
            except (ValueError, AttributeError) as e:
                print(f"Version extractions error '{version_str}': {e}")
                return None

        try:
            minVersion = "8.0.4"
            KiCadVers = version_to_tuple(pcbnew.Version())
            if not KiCadVers or KiCadVers < version_to_tuple(minVersion):
                self.print2buffer("KiCad Version: " + str(pcbnew.FullVersion()))
                self.print2buffer("Minimum required KiCad version is " + minVersion)
                self.print2buffer("This can limit the functionality of the plugin.")
        except:
            print("Error: KiCad Version check")

        if not self.config.config_is_set:
            self.print2buffer(
                "Warning: The path where the libraries should be saved has not been adjusted yet."
                + " Maybe you use the plugin in this version for the first time.\n"
            )

            additional_information = (
                "If this plugin is being used for the first time, settings in KiCad are required. "
                + "The settings are checked at the end of the import process. For easy setup, "
                + "auto setting can be activated."
            )
            self.print2buffer(additional_information)
            self.print2buffer("\n##############################\n")

    def print2buffer(self, *args):
        for text in args:
            self.print_buffer = self.print_buffer + str(text) + "\n"

    def __find_new_file__(self):
        path = self.config.get_SRC_PATH()

        if not os.path.isdir(path):
            return 0

        while True:
            newfilelist = self.folderhandler.GetNewFiles(path)
            for lib in newfilelist:
                try:
                    (res,) = self.importer.import_all(
                        lib,
                        overwrite_if_exists=self.overwriteImport,
                        import_old_format=self.import_old_format,
                    )
                    self.print2buffer(res)
                except AssertionError as e:
                    self.print2buffer(e)
                except Exception as e:
                    self.print2buffer(e)
                    backend_h.print2buffer(f"Error: {e}")
                    backend_h.print2buffer("Python version " + sys.version)
                    print(traceback.format_exc())
                self.print2buffer("")

            if not self.runThread:
                break
            if not pcbnew.GetBoard():
                # print("pcbnew close")
                break
            sleep(1)


backend_h = impart_backend()


def checkImport(add_if_possible=True):
    libnames = ["Octopart", "Samacsys", "UltraLibrarian", "Snapeda", "EasyEDA"]
    setting = backend_h.KiCad_Settings

    msg = ""

    if not backend_h.localLib:
        # DEST_PATH = self.KiCad_Project
        print("TODO checkImport")
    else:
        DEST_PATH = backend_h.config.get_DEST_PATH()
        msg += setting.check_GlobalVar(DEST_PATH, add_if_possible)

    for name in libnames:
        # The lines work but old libraries should not be added automatically
        # libname = os.path.join(DEST_PATH, name + ".lib")
        # if os.path.isfile(libname):
        #     msg += setting.check_symbollib(name + ".lib", add_if_possible)

        libdir = os.path.join(DEST_PATH, name + ".kicad_sym")
        libdir_old = os.path.join(DEST_PATH, name + "_kicad_sym.kicad_sym")
        libdir_convert_lib = os.path.join(DEST_PATH, name + "_old_lib.kicad_sym")
        if os.path.isfile(libdir):
            libname = name + ".kicad_sym"
            msg += setting.check_symbollib(libname, add_if_possible)
        elif os.path.isfile(libdir_old):
            libname = name + "_kicad_sym.kicad_sym"
            msg += setting.check_symbollib(libname, add_if_possible)

        if os.path.isfile(libdir_convert_lib):
            libname = name + "_old_lib.kicad_sym"
            msg += setting.check_symbollib(libname, add_if_possible)

        libdir = os.path.join(DEST_PATH, name + ".pretty")
        if os.path.isdir(libdir):
            msg += setting.check_footprintlib(name, add_if_possible)
    return msg


class impart_frontend(impartGUI):
    global backend_h

    def __init__(self, board: pcbnew.BOARD, action: pcbnew.ActionPlugin):
        super(impart_frontend, self).__init__(None)
        self.board = board
        self.KiCad_Project = os.path.dirname(board.GetFileName())
        self.action = action

        self.m_dirPicker_sourcepath.SetPath(backend_h.config.get_SRC_PATH())
        self.m_dirPicker_librarypath.SetPath(backend_h.config.get_DEST_PATH())

        self.SetTitle("Import Libraries")

        self.m_text.SetValue(backend_h.print_buffer)
        self.thread = None

        EVT_UPDATE(self, self.updateDisplay)

        if self.test_migrate_possible():
            self.m_button_migrate.Show()
            self.m_staticline11.Show()
            self.Layout()

    def updateDisplay(self, status):
        self.m_text.SetValue(status.data)
        self.m_text.ShowPosition(self.m_text.GetLastPosition())

    def m_checkBoxLocaLibOnCheckBox(self, event):
        backend_h.localLib = self.m_checkBoxLocaLib.GetValue()
        self.m_dirPicker_librarypath.Enable(not backend_h.localLib)

    def on_close(self, event):
        if self.thread is not None:
            self.thread.stopThread = True
            self.thread.join()
        backend_h.runThread = False
        backend_h.config.set_SRC_PATH(self.m_dirPicker_sourcepath.GetPath())
        backend_h.config.set_DEST_PATH(self.m_dirPicker_librarypath.GetPath())
        self.Destroy()

    def BottonClick(self, event):
        if not backend_h.runThread:
            backend_h.runThread = True
            backend_h.autoImport = self.m_autoImport.GetValue()
            backend_h.overwriteImport = self.m_overwrite.GetValue()
            backend_h.import_old_format = self.m_check_import_all.GetValue()
            backend_h.localLib = self.m_checkBoxLocaLib.GetValue()
            backend_h.autoLib = self.m_check_autoLib.GetValue()

            if backend_h.localLib:
                backend_h.config.set_DEST_PATH(self.KiCad_Project)
            else:
                backend_h.config.set_DEST_PATH(self.m_dirPicker_librarypath.GetPath())

            if backend_h.autoImport:
                self.thread = PluginThread(self)
                self.m_button.SetLabel("Stop")
            else:
                backend_h.__find_new_file__()
                backend_h.runThread = False
                self.m_text.SetValue(backend_h.print_buffer)
                self.m_text.ShowPosition(self.m_text.GetLastPosition())
        else:
            backend_h.runThread = False
            self.m_button.SetLabel("Start")

    def DirChange(self, event):
        backend_h.folderhandler = filehandler(self.m_dirPicker_sourcepath.GetPath())

    def ButtonManualImport(self, event):
        partnumber = self.m_textCtrl2.GetValue()
        if partnumber:
            try:
                (res,) = backend_h.importer.import_all(
                    partnumber,
                    overwrite_if_exists=self.m_overwrite.GetValue(),
                    import_old_format=self.m_check_import_all.GetValue(),
                )
                backend_h.print2buffer(res)
            except AssertionError as e:
                backend_h.print2buffer(e)
            except Exception as e:
                backend_h.print2buffer(f"Error: {e}")
                backend_h.print2buffer("Python version " + sys.version)
                print(traceback.format_exc())
            backend_h.print2buffer("")
            self.m_text.SetValue(backend_h.print_buffer)
            self.m_text.ShowPosition(self.m_text.GetLastPosition())

    def ButtonBatchImport(self, event):
        batch_text = self.m_textCtrlBatch.GetValue()
        if batch_text:
            # Split by commas and clean up whitespace
            partnumbers = [pn.strip() for pn in batch_text.split(',') if pn.strip()]
            
            for partnumber in partnumbers:
                try:
                    (res,) = backend_h.importer.import_all(
                        partnumber,
                        overwrite_if_exists=self.m_overwrite.GetValue(),
                        import_old_format=self.m_check_import_all.GetValue(),
                    )
                    backend_h.print2buffer(f"Importing {partnumber}:")
                    backend_h.print2buffer(res)
                except AssertionError as e:
                    backend_h.print2buffer(f"Error importing {partnumber}: {e}")
                except Exception as e:
                    backend_h.print2buffer(f"Error importing {partnumber}: {e}")
                    backend_h.print2buffer("Python version " + sys.version)
                    print(traceback.format_exc())
                backend_h.print2buffer("")
            
            self.m_text.SetValue(backend_h.print_buffer)
            self.m_text.ShowPosition(self.m_text.GetLastPosition())

    def test_migrate_possible(self):
        libs2migrate = self.get_old_libfiles()
        conv = convert_lib_list(libs2migrate, drymode=True)

        if len(conv):
            self.m_button_migrate.Show()
            return True
        else:
            self.m_button_migrate.Hide()
            return False

    def get_old_libfiles(self):
        libpath = self.m_dirPicker_librarypath.GetPath()
        libs = ["Octopart", "Samacsys", "UltraLibrarian", "Snapeda", "EasyEDA"]
        return find_old_lib_files(folder_path=libpath, libs=libs)

    def migrate_libs(self, event):
        libs2migrate = self.get_old_libfiles()

        conv = convert_lib_list(libs2migrate, drymode=True)

        def print2GUI(text):
            backend_h.print2buffer(text)

        if len(conv) <= 0:
            print2GUI("Error in migrate_libs()")
            return

        SymbolTable = backend_h.KiCad_Settings.get_sym_table()
        SymbolLibsUri = {lib["uri"]: lib for lib in SymbolTable}
        libRename = []

        def lib_entry(lib):
            return "${KICAD_3RD_PARTY}/" + lib

        msg = ""
        for line in conv:
            if line[1].endswith(".blk"):
                msg += "\n" + line[0] + " rename to " + line[1]
            else:
                msg += "\n" + line[0] + " convert to " + line[1]
                if lib_entry(line[0]) in SymbolLibsUri:
                    entry = SymbolLibsUri[lib_entry(line[0])]
                    tmp = {
                        "oldURI": entry["uri"],
                        "newURI": lib_entry(line[1]),
                        "name": entry["name"],
                    }
                    libRename.append(tmp)

        msg_lib = ""
        if len(libRename):
            msg_lib += "The following changes must be made to the list of imported Symbol libs:\n"

            for tmp in libRename:
                msg_lib += f"\n{tmp['name']} : {tmp['oldURI']} \n-> {tmp['newURI']}"

            msg_lib += "\n\n"
            msg_lib += "It is necessary to adjust the settings of the imported symbol libraries in KiCad."
            msg += "\n\n" + msg_lib

        msg += "\n\nBackup files are also created automatically. "
        msg += "These are named '*.blk'.\nShould the changes be applied?"

        dlg = wx.MessageDialog(
            None, msg, "WARNING", wx.KILL_OK | wx.ICON_WARNING | wx.CANCEL
        )
        if dlg.ShowModal() == wx.ID_OK:
            print2GUI("Converted libraries:")
            conv = convert_lib_list(libs2migrate, drymode=False)
            for line in conv:
                if line[1].endswith(".blk"):
                    print2GUI(line[0] + " rename to " + line[1])
                else:
                    print2GUI(line[0] + " convert to " + line[1])
        else:
            return

        if not len(msg_lib):
            return

        msg_dlg = "\nShould the change be made automatically? A restart of KiCad is then necessary to apply all changes."
        dlg2 = wx.MessageDialog(
            None, msg_lib + msg_dlg, "WARNING", wx.KILL_OK | wx.ICON_WARNING | wx.CANCEL
        )
        if dlg2.ShowModal() == wx.ID_OK:
            for tmp in libRename:
                print2GUI(f"\n{tmp['name']} : {tmp['oldURI']} \n-> {tmp['newURI']}")
                backend_h.KiCad_Settings.sym_table_change_entry(
                    tmp["oldURI"], tmp["newURI"]
                )
            print2GUI("\nA restart of KiCad is then necessary to apply all changes.")
        else:
            print2GUI(msg_lib)

        self.test_migrate_possible()  # When everything has worked, the button disappears
        event.Skip()


class ActionImpartPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        plugin_dir = Path(__file__).resolve().parent
        self.resources_dir = plugin_dir.parent.parent / "resources" / plugin_dir.name
        self.plugin_dir = plugin_dir

        self.name = "impartGUI"
        self.category = "Import library files"
        self.description = "Import library files from Octopart, Samacsys, Ultralibrarian, Snapeda and EasyEDA"
        self.show_toolbar_button = True

        self.icon_file_name = str(self.resources_dir / "icon.png")
        self.dark_icon_file_name = self.icon_file_name

    def Run(self):
        # Use virtual env
        # TODO: Does not work completely reliably
        python_executable = activate_virtualenv(venv_dir=self.plugin_dir / "venv")
        if not ensure_package("pydantic", python_executable):
            print("Problems with loading", "pydantic")
        if not ensure_package("easyeda2kicad", python_executable):
            print("Problems with loading", "easyeda2kicad")

        # Start GUI
        board = pcbnew.GetBoard()
        Impart_h = impart_frontend(board, self)
        Impart_h.ShowModal()
        Impart_h.Destroy()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None, title="KiCad Plugin")
    Impart_t = impart_frontend(None, None)
    Impart_t.ShowModal()
    Impart_t.Destroy()
