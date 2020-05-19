// ImageJ macro nrrd2tif.ijm
// Designed to open NRRD file and save as TIF
// Written by Robert Court - r.court@ed.ac.uk 


name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);

outfile = replace(name, ".nrrd", ".tif");
wait(200);
run("Nrrd ...", "load=[" + name + "]");
wait(400);
saveAs("Tiff", outfile);
wait(200);

run("Quit");
