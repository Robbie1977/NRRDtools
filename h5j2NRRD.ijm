name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
open(name);
run("Split Channels");
selectWindow("C2-" + name);
run("Nrrd ... ", "nrrd=C2-" + replace(name, ".h5j", ".nrrd"));
close();
close();
close();
run("Quit");
