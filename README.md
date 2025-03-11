# 3DPrintChangeSpool
Process G-codes to pause a 3D print before it runs out of filament.
Effective for large prints when more than one spool has to be used. For better calculations, make sure you check additional parameters.
**At this point, the script hasn't been battle-tested but is working in dry-run mode.**
For use with 1mm Nozzle, 1.75mm filament PETG, FLOW 19, 1.1 Multiplier 

I do not use the Pause command; instead, I use the Add Change Color command to simplify the spool change.

Parameters are selfexplanatory 

"C:\YourPathToPython\python.exe" "f:\YourPathToScript\color_change_plugin.py" --spool_weight 1000 --filament_diameter 1.75 --filament_density 1.25 --extrusion_mode relative --input "c:\YourPathToGcodeFile\PrintFile.gcode" --output "c:\YourPathToGcodeFileOutput\PrintFileOutput.gcode" --scale 0.015 --debug
