#!/bin/bash
# run as: align '/inputfolder/backgroundImage.nrrd' '/templatefolder/template.nrrd' '/outputfolder' ['/inputfolder/signalImage.nrrd' .... ]
# will output the both the aligned image for checking and a warp xform file
export FILE=$1
export TEMPLATE=$2
export OUTPUT=$3

export NAME=${FILE/\//_}-${TEMPLATE/\//_}

cmtk make_initial_affine --principal-axes $TEMPLATE $FILE /tmp/initial.xform

cmtk registration --initial /tmp/initial.xform --dofs 6,9 --auto-multi-levels 4 --outlist /tmp/affine.xform $TEMPLATE $FILE

rm -rf /tmp/initial.xform

cmtk warp -o $OUTPUT/$NAME-warp.xform --grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.4 --refine 4 --energy-weight 1e-1 $TEMPLATE $FILE /tmp/affine.xform

rm -rf /tmp/affine.xform

cmtk reformatx -o $OUTPUT/$NAME.nrrd --floating $FILE $TEMPLATE $OUTPUT/$NAME-warp.xform

export OTHERS=${@/$1 $2 $3 /}

for OTHER in $OTHERS;
do
  cmtk reformatx -o $OUTPUT/${OTHER/\//_}-${TEMPLATE/\//_}.nrrd --floating $OTHER $TEMPLATE $OUTPUT/$NAME-warp.xform
done
