name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
run("Nrrd ...", "load=[" + name + "]");
run("Wavefront .OBJ ...", "stack="+name+" threshold=1 resampling=2 red green blue save=[" + replace(name, ".nrrd", ".obj") + "]");
close();
run("Quit");
