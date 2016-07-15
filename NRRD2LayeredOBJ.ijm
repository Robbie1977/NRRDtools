name = getArgument;
if (name=="") exit ("No argument!");
run("Nrrd ...", "load=[" + name + "]");
file = substring(name, lastIndexOf(name, '/'));
run("Wavefront .OBJ ...", "stack=" + file + " threshold=250 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_250.obj") + "]");

run("Wavefront .OBJ ...", "stack=" + file + " threshold=150 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_150.obj") + "]");

run("Wavefront .OBJ ...", "stack=" + file + " threshold=1 resampling=2 red green blue save=[" + replace(name, ".nrrd", "_1.obj") + "]");
close();
run("Quit");
eval("script", "System.exit(0);");
