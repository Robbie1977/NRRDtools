args = split(getArgument(),",");
template=args[0];
signal=args[1];
//template="/robert/GIT/DrosAdultBRAINdomains/template/JFRCtemplate2010.nrrd"
//signal="/robert/GIT/DrosAdultBRAINdomains/individualDomainFiles/AdultBrainDomain0002.nrrd"
if (template=="") exit ("Missing template!");
if (signal=="") exit ("Missing signal!");
setBatchMode(true);
run("Nrrd ...", "load=[" + template + "]");
run("Nrrd ...", "load=[" + signal + "]");
ch1=File.getName(template);
ch2=File.getName(signal);
title=replace(replace(replace(replace(ch2,"ch2",""),"/",""),"VFBi","VFB_")," ","_");
run("Merge Channels...", "c1=" + ch1 + " c2=" + ch2 + " c3=" + ch1 + " create ignore");
run("Scale...", "x=0.2 y=0.2 z=0.2 width=204 height=102 depth=43 interpolation=Bicubic average create title="+title);
run("Z Project...", "projection=[Max Intensity]");
file=replace(signal,ch2,"thumbnail.png");
saveAs("PNG", file);
run("Quit");
eval("script", "System.exit(0);"); 
