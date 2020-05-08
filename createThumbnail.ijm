args = split(getArgument(),",");
template=args[0];
signal=args[1];
//template="/robert/GIT/DrosAdultBRAINdomains/template/JFRCtemplate2010.nrrd"
//signal="/robert/GIT/DrosAdultBRAINdomains/individualDomainFiles/AdultBrainDomain0002.nrrd"
if (template=="") exit ("Missing template!");
if (signal=="") exit ("Missing signal!");
setBatchMode(true);
run("Nrrd ...", "load=[" + template + "]");
run("Multiply...", "value=0.5 stack");
ch1=File.getName(template);
print(ch1);
run("Nrrd ...", "load=[" + signal + "]");
run("Multiply...", "value=2 stack");
ch2=File.getName(signal);
print(ch2);
title=replace(replace(replace(replace(ch2,"ch2",""),"/",""),"VFBi","VFB_")," ","_");
run("Merge Channels...", "c1=" + ch1 + " c2=" + ch2 + " c3=" + ch1 + " create ignore");
getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
getDimensions(width, height, channels, slices, frames);
print("Stack Dimentions:"+(width*voxelWidth)+" x "+(height*voxelHeight)+" x "+(slices*voxelDepth) + " " + unit);
if ((height*voxelHeight) > ((width*voxelWidth)+20)) {
  print("Reslicing from the top...");
  run("Reslice [/]...", "output="+voxelHeight+" start=Top avoid");
  getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
  getDimensions(width, height, channels, slices, frames);
  print("Stack Dimentions:"+(width*voxelWidth)+" x "+(height*voxelHeight)+" x "+(slices*voxelDepth) + " " + unit);
}else {
  if ((slices*voxelDepth) > ((width*voxelWidth)+40)) {
    print("Scaling Z...");
    scale=voxelDepth/voxelWidth;
    depth=slices*scale;
    run("Scale...", "x=1.0 y=1.0 z="+scale+" width="+width+" height="+height+" depth="+depth);
    print("Reslicing from the left...");
    run("Reslice [/]...", "output="+voxelWidth+" start=Left rotate avoid");
    getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
    getDimensions(width, height, channels, slices, frames);
    print("Stack Dimentions:"+(width*voxelWidth)+" x "+(height*voxelHeight)+" x "+(slices*voxelDepth) + " " + unit);
  }
}
run("Z Project...", "projection=[Max Intensity]");
print("Stack Dimentions:"+(width*voxelWidth)+" x "+(height*voxelHeight)+" x "+(slices*voxelDepth) + " " + unit);
if ((height*voxelHeight) > ((width*voxelWidth)+80)) {
  print("Rotating...");
  run("Rotate 90 Degrees Left");
}
run("Scale...", "x=0.2 y=0.2 width="+width+" height="+height+" interpolation=Bicubic create title="+title);
file=replace(signal,ch2,"thumbnail.png");
getDimensions(width, height, channels, slices, frames);
print("Image Dimentions:"+width+" x "+height);
saveAs("PNG", file);
run("Quit");
eval("script", "System.exit(0);"); 
