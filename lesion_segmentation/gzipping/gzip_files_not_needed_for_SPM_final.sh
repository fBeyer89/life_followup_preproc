# gzip files not needed for long workflow

for folder in `ls -dN /data/pt_life_whm/Data/LST/sub*`

do

echo $folder

if [ -f $folder/ples_lpa_mFLAIR_bl.nii ] && [ ! -f $folder/FLAIR_bl.nii.gz ];
then
echo "zipping"
gzip $folder/FLAIR_bl.nii
else echo "do nothing because nothing processed or converted already"
fi

if [ -f $folder/ples_lpa_mFLAIR_fu.nii ] && [ ! -f $folder/FLAIR_fu.nii.gz ];
then
echo "zipping"
gzip $folder/FLAIR_fu.nii
else echo "do nothing because nothing processed or converted already"
fi

if [ -f $folder/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii ];
then
echo "zipping long"
gzip $folder/*.nii
fi

if [ -f $folder/ples_lpa_mFLAIR_bl.nii ];
then
gzip $folder/ples_lpa_mFLAIR_bl.nii
gzip $folder/mFLAIR_bl.nii
echo "converting only cross runs"
else
echo "long not run"
fi

done

rm -rf /data/pt_life_whm/Data/LST/sub*/LST*/*
