#!/bin/bash
# run as: align '/inputfolder/backgroundImage.nrrd' '/templatefolder/template.nrrd' '/outputfolder' ['/inputfolder/signalImage.nrrd' .... ]
# will output the both the aligned image for checking and a warp xform file
export FILE=$1
export TEMPLATE=$2
export OUTPUT=$3

if [ ! -f $FILE ]; 
then
  echo "$FILE can not be found?"
fi

if [ ! -f $TEMPLATE ]; 
then
  echo "$TEMPLATE can not be found?"
fi

if [ ! -d $OUTPUT ]; 
then
  echo "$OUTPUT is not a directory?"
fi

export NAME=${FILE//\//_}-${TEMPLATE//\//_}
export NAME=${NAME//.nrrd/}

echo "Aligning $NAME"

cmtk make_initial_affine --principal-axes $TEMPLATE $FILE /tmp/$NAME-initial.xform

cmtk registration --initial /tmp/$NAME-initial.xform --dofs 6,9 --auto-multi-levels 4 --outlist /tmp/$NAME-affine.xform $TEMPLATE $FILE

rm -rf /tmp/$NAME-initial.xform

cmtk warp -o $OUTPUT/$NAME-warp.xform --grid-spacing 80 --exploration 30 --coarsest 4 --accuracy 0.4 --refine 4 --energy-weight 1e-1 $TEMPLATE $FILE /tmp/$NAME-affine.xform

rm -rf /tmp/$NAME-affine.xform

export OTHERS=${@/$1 $2 $3 /}

for OTHER in $OTHERS;
do
  export FILE=${OTHER//\//_}-${TEMPLATE//\//_}
  export FILE=${FILE//.nrrd/}
  cmtk reformatx -o $OUTPUT/${FILE}.nrrd --floating $OTHER $TEMPLATE $OUTPUT/$NAME-warp.xform
done
