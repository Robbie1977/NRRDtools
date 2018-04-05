name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
open(name);
wait(500);
otitle = getTitle();
run("Split Channels");
while(isOpen(1)) {
	ntitle = getTitle();
	run("Nrrd ... ", "nrrd=" + replace(replace(name,otitle,ntitle), ".h5j", ".nrrd"));
	close();
	wait(10);
}
run("Quit");
