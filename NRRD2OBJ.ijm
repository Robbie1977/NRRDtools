name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
run("Nrrd ...", "load=[" + name + "]");
run("Wavefront .OBJ ...", "stack=volume.nrrd threshold=1 resampling=4 red green blue save=[" + replace(name, ".nrrd", ".obj") + "]");
close();
run("Quit");
