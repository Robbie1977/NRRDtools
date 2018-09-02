arg = getArgument();
if (arg=="") exit ("Missing signal!");
setBatchMode(true);
run("Nrrd ...", "load=[" + arg + "]");
run("Multiply...", "value=2 stack");
run("Z Project...", "projection=[Max Intensity]");
getDimensions(width, height, channels, slices, frames); 
run("Scale...", "x=0.2 y=0.2 width=&width height=&height interpolation=Bicubic create");
file=replace(arg,".nrrd",".png");
saveAs("PNG", file);
run("Quit");
eval("script", "System.exit(0);"); 
