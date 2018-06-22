name = getArgument;
if (name=="") exit ("No argument!");
setBatchMode(true);
open(name);
wait(500);
otitle = getTitle();
dotIndex = indexOf(otitle, "."); 
oExt = substring(otitle, dotIndex); 
run("Split Channels");
test = isOpen(1)+isOpen(2)+isOpen(3);

while(test>0) {
	ntitle = getTitle();
	run("Nrrd ... ", "nrrd=" + replace(replace(name,otitle,ntitle), oExt, "-"+test+".nrrd"));
	close();
	wait(500);
	test=test-1;
}
run("Quit");
eval("script", "System.exit(0);");
exit();
