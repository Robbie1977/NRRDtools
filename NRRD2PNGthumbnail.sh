echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/createThumbnail.ijm'
echo 'export TEMPLATE=path/VFB/t/001/background.nrrd'
echo 'run in the directory above the volume.nrrd files'
echo '-f forces thumbnail recreation'
echo '-h runs in headless mode using xvfb-run'
OPTIONS=$1
for file in $(pwd)/*/volume.nrrd
do
  echo "Checking $file"
  if [ -f $file ]
  then
    if [ -f "${file/volume.nrrd/thumbnail.png}" ] && [[ "$OPTIONS" != *"f"* ]] && [ "$MACRO" -ot "${file/volume.nrrd/thumbnail.png}" ]
    then
      echo PNG file already exists! Skipping..
    else
      echo processing ${file}...
      # if forcing overwite then delete the old copy
      if [[ "$OPTIONS" = *"f"* ]]
      then
        rm "${file/volume.nrrd/thumbnail.png}"
      fi
      export MatchTP=$file
      for background in ${TEMPLATE/001/00*}
      do 
        if [ "$(head $file | grep sizes)" == "$(head $background | grep sizes)" ]
        then 
          export MatchTP=$background
          echo "$file = $MatchTP"
        fi
      done
      if [ "$(head $file | grep sizes)" == "$(head $MatchTP | grep sizes)" ]
      then
         # generate thumbnail using Fiji/ImageJ
         echo "Generating thumbnail from $MatchTP,$file"
        if [[ "$OPTIONS" = *"h"* ]]
        then
          xvfb-run -w 20 $FIJI -macro $MACRO "$MatchTP,$file"
        else
          $FIJI -macro $MACRO "$MatchTP,$file"
        fi
      else 
        echo "Template not found for ${file}! Skipping.."
      fi  
    fi
  else
    echo "Broken link for ${file}! Skipping.."
  fi
done
