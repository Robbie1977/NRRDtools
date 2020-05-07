args = split(getArgument(),",");
x=args[0];
y=args[1];
z=args[2];
inFile=args[3];
outFile="";
if (args.length > 4) {
    outFile=args[4];
}
if (x=="") exit("Missing x scale value! expecting: x,y,z,in[,out]");
if (y=="") exit("Missing y scale value! expecting: x,y,z,in[,out]");
if (z=="") exit("Missing z scale value! expecting: x,y,z,in[,out]");
if (inFile=="") exit("Missing input file! expecting: x,y,z,in[,out]");
if (outFile=="") {
    outFile=replace(inFile,".nrrd","_20X.nrrd");
}
setBatchMode(true);
run("Nrrd ...", "load=[" + inFile + "]");
inTitle=File.getName(inFile);
print(inTitle);
outTitle=replace(inTitle,".nrrd","_20X.nrrd");
getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
getDimensions(width, height, channels, slices, frames);
newWidth=(width * parseFloat(x));
newHeight=(height * parseFloat(y));
newDepth=(slices * parseFloat(z));
newWidth = round(newWidth);
newHeight = round(newHeight);
newDepth = round(newDepth);
print("Scalling from [" + width + "," + height + "," + slices + "] to [" + newWidth + "," + newHeight + "," + newDepth + "]...");
run("Scale...", "x="+x+" y="+y+" z="+z+" width="+newWidth+" height="+newHeight+" depth="+newDepth+" interpolation=Bicubic average process create title=" + outFile);
print("Saving to " + outFile);
run("Nrrd ... ", "nrrd=" + outFile);

run("Quit");
eval("script", "System.exit(0);"); 
