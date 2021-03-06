echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/NRRD2LayeredOBJ.ijm'
echo 'run in the directory above the volume.nrrd files'
echo '-f forces recreation'
echo '-h runs in headless mode using xvfb-run'
for file in ./*/volume.nrrd
do
  if [ -f $file ]
  then
    if [ -e ${file/.nrrd/.obj} ] && [ "$1" != "-f" ] && [ $MACRO -ot ${file/.nrrd/.obj} ] && [ ${MACRO/.ijm/.sh} -ot ${file/.nrrd/.obj} ]
    then
      echo recent OBJ file already exists! Skipping..
    else
      echo processing $(pwd)${file/.\//\/}...
      # if forcing overwite then delete the old copy
      if [ "$1" == "-f" ] 
      then
        rm ${file/.nrrd/.obj}
      fi
      # generate thresholded surfaces using Fiji/ImageJ
      if [[ $1 == *"h"* ]]
      then
        xvfb-run -w 10 $FIJI -macro $MACRO $file
      else
        $FIJI -macro $MACRO $file
      fi
      if [ -f ${file/.nrrd/_250.obj} ]
      then
        # add basic file header
        echo '# Merge of thresholded surface wavefront .obj without sufaces at 1, 150 and 250 for VirtualFlyBrain.org.' > ${file/.nrrd/.tmp}
        echo '# Original data generated by the ExportMesh_ plugin in ImageJ.' >> ${file/.nrrd/.tmp}
        # merge surface points together (only taking verticies not faces then only 1/8th at threshold of 1, Half at 150 threshold and all at 250)
        cat ${file/.nrrd/_1.obj} | grep 'v ' | sed -n '1~2!p' | sed -n '1~2!p' | sed -n '1~2!p' | sed -n '1~2!p' >> ${file/.nrrd/.tmp}
        cat ${file/.nrrd/_150.obj} | grep 'v ' | sed -n '1~2!p' >> ${file/.nrrd/.tmp}
        cat ${file/.nrrd/_250.obj} | grep 'v ' >> ${file/.nrrd/.tmp}
        # remove thresholded surfaces
        rm ${file/.nrrd/_*.obj}
        # remove any duplicate points
        awk '!a[$0]++' ${file/.nrrd/.tmp} > ${file/.nrrd/.obj}
        # remove the temp file
        rm ${file/.nrrd/.tmp}
      fi
    fi
  else
    echo Broken file ${file}! Skipping...
  fi
done
