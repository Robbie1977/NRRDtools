echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/createThumbnail.ijm'
echo 'export TEMPLATE=path/VFB/t/001/background.nrrd'
echo 'run in the directory above the volume.nrrd files'
for file in ./*/volume.nrrd
do
  if [ -f $file ]
  then
    if [ -e ${file/volume.nrrd/thumbnail.png} ] && [ "$1" != "-f" ] && [ $MACRO -ot $ ${file/volume.nrrd/thumbnail.png} ] && [ ${MACRO/createThumbnail.ijm/NRRD2PNGthumbnail.sh} -ot $ ${file/volume.nrrd/thumbnail.png} ]
    then
      echo PNG file already exists! Skipping..
    else
      echo processing ${file}...
      # if forcing overwite then delete the old copy
      if [ "$1" == "-f" ]
      then
        rm ${file/volume.nrrd/thumbnail.png}
      fi
      # generate thresholded surfaces using Fiji/ImageJ
      xvfb-run $FIJI -macro $MACRO "$TEMPLATE,$file"
    fi
  else
    echo Broken link for ${file}! Skipping..
  fi
done
