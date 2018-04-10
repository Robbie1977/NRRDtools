echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/resizeNRRDtoJFRC2.ijm'
echo 'run in the directory above the volume.nrrd files'
echo '-f forces recreation'
echo '-h runs in headless mode using xvfb-run'
for file in $(pwd)/*/*.nrrd
do
  echo $file
  if [ -f $file ]
  then
    if [ $(head $file | grep "sizes: 1025 513 218" | wc -l) -gt 0 ] 
    then
      echo processing $(pwd)${file/.\//\/}...
      # resize nrrd
      if [[ $1 == *"h"* ]]
      then
        timeout 15m xvfb-run -w 10 $FIJI -macro $MACRO $file
        pkill Xvfb
      else
        timeout 15m $FIJI -macro $MACRO $file
      fi
      sleep 5s
    fi
  else
    echo Broken file ${file}! Skipping...
  fi
done
