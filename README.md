![Static Badge](https://img.shields.io/badge/Supports_KiCad-v6%2C_v7%2C_v8-%23314cb0)
![Static Badge](https://img.shields.io/badge/Supports-Windows%2C_Mac%2C_Linux-Green)

[![Static Badge](https://img.shields.io/badge/Samacsys-Works_(Component_Search_Engine)-1e8449)](https://componentsearchengine.com/)
[![Static Badge](https://img.shields.io/badge/SnapEDA-Works_(v4%2C_v6)-27ae60)](https://www.snapeda.com/home/)
[![Static Badge](https://img.shields.io/badge/UltraLibrarian-Works-229954)](https://app.ultralibrarian.com/search)
[![Static Badge](https://img.shields.io/badge/Octopart-Works-52be80)](https://octopart.com/)
[![Static Badge](https://img.shields.io/badge/LCSC--EasyEDA-Works-008000)](https://www.lcsc.com/)

[![GitHub Release](https://img.shields.io/github/release/Steffen-W/Import-LIB-KiCad-Plugin.svg)](https://github.com/Steffen-W/Import-LIB-KiCad-Plugin/releases/latest)
[![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/Steffen-W/Import-LIB-KiCad-Plugin/total)](https://github.com/Steffen-W/Import-LIB-KiCad-Plugin/releases/latest/download/Import-LIB-KiCad-Plugin.zip)

# KiCad Import-LIB-KiCad-Plugin ![icon](plugins/icon_small.png)

This plugin allows importing downloaded libraries from the platforms [Octopart](https://octopart.com/), [Samacsys](https://componentsearchengine.com/), [Ultralibrarian](https://app.ultralibrarian.com/search), [Snapeda](https://www.snapeda.com/home/) and [EasyEDA](https://www.lcsc.com/). It can import symbols, footprints, descriptions, and if available, 3D files. Normally, when you select the imported symbol in KiCad, the appropriate footprint and the 3D file should also be linked. Provided, of course, that the libraries have been included as specified below.

[![SC2 Video](doc/demo.gif)]([https://youtu.be/cdOKDY-F4ZU](https://youtu.be/VrWPPHtCovQ))

[YouTube - Instructions for installation and use](https://youtu.be/BYIKjCs1qKQ)

## Installation

Install the plugin easily through KiCad's **Plugin And Content Manager**. Select ![icon](plugins/icon_small.png) **Import-LIB-KiCad-Plugin** in the Plugins tab, press **Install** and then **Apply Pending Changes**.

You can also download the latest version [here](https://github.com/Steffen-W/Import-LIB-KiCad-Plugin/releases/latest/download/Import-LIB-KiCad-Plugin.zip) and install it via **KiCad** -> **Plugin And Content Manager** -> **Install from File...** -> select **Import-LIB-KiCad-Plugin.zip** and import.

## Use of the application

The import window is accessible in the **PCB Editor** -> **Tools** -> **External Plugins** -> **impartGUI**

![Screenshot_GUI](doc/2024-08-17_Example_Import.png)

The libraries to import must be located in the folder specified as **Folder of the library** to import. After pressing Start, the libraries will be imported into the specified folder (**Library save location**). Provided that the paths have been [added correctly in KiCad](#including-the-imported-libraries-in-kicad), the parts can be used immediately in KiCad. If the libraries have not been imported correctly, a warning will indicate this.

### Import Methods

There are three ways to import components:

1. **Manual Import**: Enter a single part number in the text field and click "Manual Import" or press Enter.
2. **Batch Import**: Enter multiple part numbers separated by commas in the batch import text area and click "Import Batch". This allows you to import multiple components in one go.
3. **Automatic Import**: Enable "auto background import" to automatically import any new library files that appear in the specified import folder.

### Deutsche Übersetzung / German Translation

#### Importmethoden

Es gibt drei Möglichkeiten, Komponenten zu importieren:

1. **Manueller Import**: Geben Sie eine einzelne Teilenummer in das Textfeld ein und klicken Sie auf "Manual Import" oder drücken Sie Enter.
2. **Batch-Import**: Geben Sie mehrere, durch Kommas getrennte Teilenummern in den Batch-Import-Textbereich ein und klicken Sie auf "Import Batch". Dies ermöglicht es Ihnen, mehrere Komponenten auf einmal zu importieren.
3. **Automatischer Import**: Aktivieren Sie "auto background import", um automatisch alle neuen Bibliotheksdateien zu importieren, die im angegebenen Importordner erscheinen.

## Including the imported libraries in KiCad
To use the imported libraries from the plugin, you will need to add a couple entries to KiCad's path first to see them. You can either let the plugin make the changes automatically (auto KiCad setting) or set the following changes manually in KiCad.

**Preferences** -> **Configure paths** -> **Environment Variables** -> Add the following entry
|Name            |Path    |
|----------------|--------|
|KICAD_3RD_PARTY |**YourLibraryFolder**/KiCad |

**Preferences** -> **Manage Symbol Libraries** -> **Global Libraries** -> Add the following entries
**(Note: Errors will show up if components weren't imported yet. The errors will disappear after importing as libraries will be created)**
|Active            |Visible           |Nickname       |Library Path                                 | Library Format |
|------------------|------------------|---------------|---------------------------------------------|----------------|
|:heavy_check_mark:|:heavy_check_mark:|Samacsys       |${KICAD_3RD_PARTY}/Samacsys.kicad_sym        | KiCad          |
|:heavy_check_mark:|:heavy_check_mark:|Snapeda        |${KICAD_3RD_PARTY}/Snapeda.kicad_sym         | KiCad          |
|:heavy_check_mark:|:heavy_check_mark:|UltraLibrarian |${KICAD_3RD_PARTY}/UltraLibrarian.kicad_sym  | KiCad          |
|:heavy_check_mark:|:heavy_check_mark:|EasyEDA        |${KICAD_3RD_PARTY}/EasyEDA.kicad_sym         | KiCad          |

**Preferences** -> **Manage Footprint Libraries** -> **Global Libraries** -> Add the following entries
**(Note: It is best to add the library only after the import has been done with the plugin. Afterwards only the created libraries have to be imported. Lower entries are only for example.)**
|Active             |Nickname       |Library Path                             | Library Format|
|-------------------|---------------|-----------------------------------------|---------------|
|:heavy_check_mark: |Samacsys       | ${KICAD_3RD_PARTY}/Samacsys.pretty      | KiCad         |
|:heavy_check_mark: |Snapeda        | ${KICAD_3RD_PARTY}/Snapeda.pretty       | KiCad         |
|:heavy_check_mark: |UltraLibrarian | ${KICAD_3RD_PARTY}/UltraLibrarian.pretty| KiCad         |
|:heavy_check_mark: |EasyEDA        | ${KICAD_3RD_PARTY}/EasyEDA.pretty       | KiCad         |

## Migrate the libraries

It is strongly recommended to migrate the libraries. If you see the "migrate the libraries" button, you have been using the plugin for some time. From now on, only the latest library format will be supported. If this does not work, the old format will continue to work.

![GUI_migrate](doc/2024-08-17_GUI_migrate.png)

By pressing "migrate the libraries" the following window appears. Depending on how many libraries you use, fewer libraries may be displayed. Now you can start the conversion process. Important: The conversion only works completely from KiCad 8.0.4. If possible, use the latest stable [![GitHub Release](https://img.shields.io/badge/KiCad-V8-blue.svg)](https://www.kicad.org/download/) version. 

![Migration](doc/2024-08-17_Migration.png)

Depending on the setup, further changes may be necessary. You will be notified if this is necessary. Press ok to apply them. A restart of KiCad is mandatory to apply the changes.

![update setting](doc/2024-08-17_setting.png)

## CLI Support

The import process can also be done completely without the GUI. ```python plugins/KiCadImport.py```

```bash
usage: KiCadImport.py [-h] (--download-folder DOWNLOAD_FOLDER | --download-file DOWNLOAD_FILE) --lib-folder LIB_FOLDER [--overwrite-if-exists] [--path-variable PATH_VARIABLE]

Import KiCad libraries from a file or folder.

options:
  -h, --help            show this help message and exit
  --download-folder DOWNLOAD_FOLDER
                        Path to the folder with the zip files to be imported.
  --download-file DOWNLOAD_FILE
                        Path to the zip file to import.
  --lib-folder LIB_FOLDER
                        Destination folder for the imported KiCad files.
  --overwrite-if-exists
                        Overwrite existing files if they already exist
  --path-variable PATH_VARIABLE
                        Example: if only project-specific '${KIPRJMOD}' standard is '${KICAD_3RD_PARTY}'
```

## Warranty

**None. Zero. Zilch. Use at your own risk**, and please be sure to use git or some other means of backing up/reverting changes caused by this script. This script will modify existing lib, dcm, footprint or 3D model files. It is your responsibility to back them up or have a way to revert changes should you inadvertently mess something up using this tool.

Please write an issues if an import does not work as requested.

## FAQ

**Do I have to manually create a library that does not yet exist before using the plugin?**
No, you do not need to create a file manually. Your only task is to download your desired part from the internet and start the import process with the plugin.

**Where can I save the library?**
It is possible to save the files in any place on your PC where you have read and write permissions.
It is also possible to store the files on network drives or cloud storage to share the library with others.
In the libraries relative paths are used, the absolute path is not considered.

**Can I change the storage location?**
Yes, this is of course always possible. But you should keep in mind that the existing libraries will not be moved automatically. You would have to do that yourself if necessary.

**If I import from one source, do I have to stay with that source, or can I import from all sources?**
For each source, a separate library is created for KiCad. Maximum actually three (Samacsys, Ultralibrarian and Snapeda), Octopart components as well as from other suppliers can be found in the Snapeda library. So if you import from a new source, a new library can be created. But maximum three.

**Why are there two symbol libraries?**
In the latest version both the old and the "new" (since KiCad 6) symbol library format is imported. It is possible to prevent this by deselecting "import also old format". An automatic conversion from the old to the new format should only be done if you are an experienced KiCad user.

### General KiCad Questions

**I have entered a library in the settings in KiCad that does not exist at this time, what happens?**
You get a message that this library does not exist. Nothing more. As soon as it exists, it can be accessed.

**Can I remove a library from the settings?**
Yes, you can always do that. The libraries are neither deleted nor edited in any way. They are just not included.

## Todo List

- [ ] Add digikey support
- [ ] Reloading the dependency pydantic for [uPesy/easyeda2kicad.py](https://github.com/uPesy/easyeda2kicad.py)
- [ ] Updating the library before an import `kicad-cli sym upgrade`
- [ ] Updating the footprint library `kicad-cli fp upgrade *.pretty`
- [x] add [jlcpcb parts](https://jlcpcb.com/parts) to import (integrate [uPesy/easyeda2kicad.py](https://github.com/uPesy/easyeda2kicad.py))
- [x] Automatic background import
- [x] Test on a Mac
- [x] Testing all library formats
- [x] Using the new KiCad format
- [x] Possibility of automatic KiCad settings adjustment

If you notice an error then please write me an issue. If you want to change the GUI or the functionality, I am also open for ideas.

[![Create Issue](https://img.shields.io/badge/Create%20Issue-blue.svg)](https://github.com/Steffen-W/Import-LIB-KiCad-Plugin/issues/new)

<a href="https://ko-fi.com/steffenw1" target="_blank"><img src="https://storage.ko-fi.com/cdn/brandasset/kofi_button_stroke.png" alt="Support via Ko-fi" height="30"></a>

## Many thanks to

[wexi with impart](https://github.com/wexi/impart) and [topherbuckley](https://github.com/topherbuckley/kicad_remote_import) for the code on which the GUI is based.
I would also like to thank [uPesy](https://github.com/uPesy) for enabling the import of [EasyEDA](https://www.lcsc.com/) through his python project [uPesy/easyeda2kicad.py](https://github.com/uPesy/easyeda2kicad.py) (AGPL-3.0 license).
I also thank the people who helped me find the errors in the code.
