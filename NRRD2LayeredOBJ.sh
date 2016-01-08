echo 'before running specify the fiji executable and macro (located in this dir):'
echo 'export FIJI=path/fiji'
echo 'export MACRO=ThisDir/NRRD2LayeredOBJ.ijm'
echo 'run in the directory above the volume.nrrd files'
for file in ./*/volume.nrrd
do
  $FIJI macro $MACRO $file batch
  echo '# Merge of thresholded surface wavefront .obj without sufaces at 1, 150 and 250 for VirtualFlyBrain.org.' > volume.obj
  echo '# Original data generated by the ExportMesh_ plugin in ImageJ.' >> volume.obj
  cat volume_*.obj | grep 'v ' >> volume.obj
  rm volume_*.obj
done
