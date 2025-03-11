# 3DPrintChangeSpool
Process G-codes to pause a 3D print before it runs out of filament.
Effective for large prints when more than one spool has to be used. For better calculations, make sure you check additional parameters.
**At this point, the script hasn't been battle-tested but is working in dry-run mode.**

Parameters are selfexplanatory 

"C:\YourPathToPython\python.exe" "f:\YourPathToScript\color_change_plugin.py" --spool_weight 1000 --filament_diameter 1.75 --filament_density 1.25 --extrusion_mode relative --input "c:\YourPathToGcodeFile\PrintFile.gcode" --output "c:\YourPathToGcodeFileOutput\PrintFileOutput.gcode" --debug
