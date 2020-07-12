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
X=(width*voxelWidth);
Y=(height*voxelHeight);
Z=(slices*voxelDepth);
print("Stack Dimentions:"+X+" x "+Y+" x "+Z + " " + unit);
if (Z > X) {
  print("Rotaing +90degrees about the Y axis");
  run("TransformJ Rotate", "z-angle=0.0 y-angle=90 x-angle=0.0 interpolation=Linear background=0.0 adjust");
  X1=Z;
  Y1=Y;
  Z1=X;
}else{
  X1=X;
  Y1=Y;
  Z1=Z;
}
if (Z1 > Y1) {
  print("Rotaing +90degrees about the X axis");
  run("TransformJ Rotate", "z-angle=0.0 y-angle=0.0 x-angle=90 interpolation=Linear background=0.0 adjust");
  X2=X1;
  Y2=Z1;
  Z2=Y1;
}else{
  X2=X1;
  Y2=Y1;
  Z2=Z1;
}
if (Y2 > X2) {
  print("Rotaing -90degrees about the Z axis");
  run("TransformJ Rotate", "z-angle=-90 y-angle=0.0 x-angle=0.0 interpolation=Linear background=0.0 adjust");
  X3=Y2;
  Y3=X2;
  Z3=Z2;
}else{
  X3=X2;
  Y3=Y2;
  Z3=Z2;
}
getVoxelSize(voxelWidth, voxelHeight, voxelDepth, unit);
getDimensions(width, height, channels, slices, frames);
print("Stack Dimentions:"+(width*voxelWidth)+" x "+(height*voxelHeight)+" x "+(slices*voxelDepth) + " " + unit);

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
