echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/h5j2NRRD.ijm'
echo 'run in the directory above the volume.nrrd files'
echo '-f forces recreation'
echo '-h runs in headless mode using xvfb-run'
for file in $(pwd)/*/*.h5j
do
  echo $file
  if [ -f $file ]
  output=${file/.h5j/.nrrd}
  output=$(echo $output|sed 's|\(.*\)/|\1/C1-|')
  echo $output
  then
    if [ -e ${output} ] && [ "$1" != "-f" ] 
    then
      echo recent nrrd file already exists! Skipping..
    else
      echo processing $(pwd)${file/.\//\/}...
      # if forcing overwite then delete the old copy
      if [ "$1" == "-f" ] 
      then
        rm ${file/.h5j/.nrrd}
      fi
      # convert n5j into nrrd
      if [[ $1 == *"h"* ]]
      then
        xvfb-run -w 10 $FIJI -macro $MACRO $file
        pkill Xvfb
      else
        $FIJI -macro $MACRO $file
      fi
      sleep 5s
    fi
  else
    echo Broken file ${file}! Skipping...
  fi
done
