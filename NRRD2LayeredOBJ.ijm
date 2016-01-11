name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
run("Nrrd ...", "load=[" + name + "]");
run("Wavefront .OBJ ...", "stack=volume.nrrd threshold=250 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_250.obj") + "]");

run("Wavefront .OBJ ...", "stack=volume.nrrd threshold=150 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_150.obj") + "]");

run("Wavefront .OBJ ...", "stack=volume.nrrd threshold=1 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_1.obj") + "]");
close();
run("Quit");
