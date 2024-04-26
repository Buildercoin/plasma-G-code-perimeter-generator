# plasma-G-code-perimeter-generator
CNC plasma G-code perimeter generator
Hi ,
this little software will take a g-code.TXT file find the furthest X and Y, generate a g-code to dry run only to does x and y, come back to 0,0 and then pause till cycle start or cancel.
you are also able to choose your favorite feed for that dry run.
it's currently only supporting Post processor: Centroid Acorn Plasma THC.scpost and you can find it in sheetcam if needed.

if for any reason you want to change the feed once the code have been generated and saved you can modify the feed reload the files and it will over write the previous feed only for that "macro". 


if you have a cnc plasma with a different controler then acorn let me know which post processor that you use if it's in the sheetcam list or send it to me via email at waxer.master@gmail.com.
also if you have idea or feature that would be nice to add let me know and i'll see what i can do. 

on that, i Hope it will save you some time over conventional dry run.
