echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/NRRD2LayeredOBJ.ijm'
echo 'run in the directory above the volume.nrrd files'
for file in ./*/volume.nrrd
do
  if [ -e ${file/.nrrd/.obj} ]
  then
    echo OBJ file already exists! Skipping..
  else
    echo processing ${file}...
    # generate thresholded surfaces using Fiji/ImageJ
    $FIJI --headless --console $MACRO $file
    # add basic file header
    echo '# Merge of thresholded surface wavefront .obj without sufaces at 1, 150 and 250 for VirtualFlyBrain.org.' > ${file/.nrrd/.obj}
    echo '# Original data generated by the ExportMesh_ plugin in ImageJ.' >> ${file/.nrrd/.obj}
    # merge surface points together
    cat ${file/.nrrd/_*.obj} | grep 'v ' > ${file/.nrrd/.tmp}
    # remove thresholded surfaces
    rm ${file/.nrrd/_*.obj}
    # remove any duplicate points
    awk '!a[$0]++' ${file/.nrrd/.tmp} >> ${file/.nrrd/.obj}
    # remove the temp file
    rm ${file/.nrrd/.tmp}
  fi
done
