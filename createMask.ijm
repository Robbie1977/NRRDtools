
name = getArgument;
if (name=="") exit ("No argument!");
run("Nrrd ...", "load=" + name);
wait(1000);
setSlice(128);
//getBoolean("OK stack level?");
setOption("BlackBackground", true);
wait(1000);
run("Make Binary", "method=RenyiEntropy background=Dark black thresholded remaining");
wait(1000);
run("Despeckle", "stack");
wait(1000);
Nname = replace(name,".nrrd","-mask-despeckle.nrrd");
wait(1000);
run("Nrrd ... ", "nrrd=[" + Nname + "]");
wait(1000);
close();
