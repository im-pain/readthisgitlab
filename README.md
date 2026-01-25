# KKBP Importer

![image](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/readme.jpg)

This is a plugin pack for exporting Koikatsu cards to Blender.  

The ```KKBP Exporter``` exports the card's textures, mesh and armature from the game. The ```KKBP Importer``` uses that data to setup the character in Blender.  
Imported characters can be used in Blender for animations, renders, etc. They can also be converted to FBX files to use in other programs. 

* **[Download](https://gitgoon.dev/kkbp-dev/KKBP_Importer/releases)**
* **[Alternate download](https://gitgoon.dev/kkbp-dev/KKBP_Importer/archive/refs/heads/master.zip)** (this is a live snapshot of the repo that might not work!) 

## Features
* Near perfect mesh and texture replication
* All face / tear / cartoon eye expressions available as shape keys
* Can import animations and poses from the game
* Works in EEVEE and Cycles
* Fully featured Rigify armature
* Export the model as .fbx for Unity VRM or Unreal Engine
* Easily edit colors for most materials, just like in the game!
* SFW mode 

## Video walkthrough of the plugins

[(Click for playlist!)  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/readmeyt.png)](https://www.youtube.com/watch?v=VqhpOlonCEY&list=PLhiuav2SCuvf8u0UW5NWhGOxqKeAc5lfJ&index=1)

## How to use it

#### Export the card from Koikatsu
<details>
  <summary> (click to show export instructions)</summary>

1. Install the dependencies  
    * The easiest way to mod your game and install all dependencies is the **[HF Patch for Koikatsu](https://github.com/ManlyMarco/KK-HF_Patch)** or the **[HF Patch for Koikatsu Sunshine](https://github.com/ManlyMarco/KKS-HF_Patch)**  
    * If you are already using the pre-modded **Better Repack**, you need to do one of the following:  
      * manually install the "Character Maker Poses" zipmod  
          * [Koikatsu link](https://sideload.betterrepack.com/download/KKEC/Sideloader%20Modpack%20-%20Exclusive%20KK/DeathWeasel%20AKA%20Anon11/)  
          * [Koikatsu Sunshine link](https://sideload.betterrepack.com/download/KKEC/Sideloader%20Modpack%20-%20Exclusive%20KKS/DeathWeasel/)  
      * OR, update your mods using the auto-updater in the launcher  
      * OR, install the HF patch over the repack  
    * If your game is already modded, but you don't want to install the HF patch, just install KKAPI, KK Accessory States, KK Pushup, and the poses zipmod linked above

1. Find your Koikatsu install directory and drag the **[KKBP exporter .dll](https://gitgoon.dev/kkbp-dev/KKBP_Exporter/releases)** into the /bepinex/plugins/ folder

1. Start Koikatsu and open the Character Maker
   
1. Enable the KKBP Exporter window.  
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/export.jpg)

1. Click the "Export Model for KKBP" button at the top of the screen. 
    * This may take a few minutes depending on your computer hardware. 
    * [An explanation of all export options can be found here](https://gitgoon.dev/kkbp-dev/KKBP_Importer/src/branch/master/wiki/readme.md#exporter-panel-settings)   
   
3. A folder in your Koikatsu install directory will popup when the export is finished
</details>

#### Import the model to Blender
<details>
  <summary> (click to show import instructions)</summary>

1. Open Blender 5.0. **Other versions are not guaranteed to work.** [Click here if you are not using Blender 5.0](https://gitgoon.dev/kkbp-dev/KKBP_Importer/src/branch/master/wiki)
   
1. Install **[mmd_tools](https://extensions.blender.org/add-ons/mmd-tools/)** in Blender
   
1. Install **[KKBP Importer 9.0](https://gitgoon.dev/kkbp-dev/KKBP_Importer/releases)** in Blender
   
1. After you install both addons, you can click the "Import model" button in the KKBP panel. 
    * [An explanation of all import options can be found here](https://gitgoon.dev/kkbp-dev/KKBP_Importer/src/branch/master/wiki/readme.md#import-panel-options)   
    * ![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/import.jpg)

1. Choose the .pmx file from the export folder 
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/select_pmx.jpg)

1. The blender console will appear and begin importing the model. This may take a few minutes depending on your computer hardware  
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/console.jpg)

1. Check there were no errors during import in the scripting tab. A successful import will end in "KKBP import finished in XX minutes"  
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/error.jpg)

</details>

#### (Optional) Exporting as fbx
<details>
  <summary> (click to show fbx export instructions)</summary>

1. If you want to reduce the bone count, or convert the model's armature for VRM / VRChat / Unreal Engine, click the "Prep for target application" button in the KKBP panel.  This will also create an atlas file for your body / hair / clothes and save them to the atlas_files folder in your export folder

1. After you click the button, hide the original collection in the outliner and show the new collection  
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/show_atlas.jpg)

1. Click the export button in the collection tab to export an fbx file to the atlas_files folder in the export folder  
![ ](https://gitgoon.dev/kkbp-dev/KKBP_Importer/raw/branch/master/wiki/export_fbx.jpg)
</details>


## Help

[Check the wiki for FAQ and basic info.](https://gitgoon.dev/kkbp-dev/KKBP_Importer/src/branch/master/wiki/)  
I also setup a [Discord](https://discord.gg/NU53kH8ngw) for general discussion / help  
If you're still having trouble please [create a new issue](https://gitgoon.dev/kkbp-dev/KKBP_Importer/issues)  

## Contributing

Any contributions are welcome! Please check out the links below:
* [The issues page](https://gitgoon.dev/kkbp-dev/KKBP_Importer/issues)
* [Make a pull request](https://gitgoon.dev/kkbp-dev/KKBP_Importer/pulls)
* [Translate the KKBP interface](https://gitgoon.dev/kkbp-dev/KKBP_Importer/src/branch/master/interface)  

## Similar Projects

* [KKBP Exporter](https://gitgoon.dev/kkbp-dev/KKBP_Exporter) - The exporter plugin for this project
* [SKLX-creator](https://www.patreon.com/posts/sklx-lite-118039975) - Export Koikatsu cards to Blender
* [KKPMX](https://github.com/CazzoPMX/KKPMX) - Export Koikatsu cards to MMD
* [Koikatsu Pmx Exporter (Reverse Engineered & updated)](https://github.com/Snittern/KoikatsuPmxExporterReverseEngineered) - The original Koikatsu mesh exporter decompiled and updated
* [SVS CharacterExporter](https://github.com/Sonogami-Rinne/SVS_CharacterExporter) - An experimental character exporter for Summer Vacation Scramble
