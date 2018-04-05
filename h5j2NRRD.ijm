name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
open(name);
wait(500);
otitle = getTitle();
run("Split Channels");
test = isOpen(1)+isOpen(2)+isOpen(3);

while(test>0) {
	getTitle();
	ntitle = getTitle();
	run("Nrrd ... ", "nrrd=" + replace(replace(name,otitle,ntitle), ".h5j", ".nrrd"));
	close();
	wait(500);
	test=test-1;
	print(test);
}
eval("script", "System.exit(0);");