# gzip files not needed for long workflow

for folder in `ls -dN /data/pt_life_whm/Data/LST/sub*`

do

echo $folder/ples_lpa_mFLAIR_bl.nii

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

if [ ! -f $folder/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz ] && [ ! -f $folder/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii ] && [ -f $folder/mFLAIR_fu.nii.gz ] && [ -f $folder/mFLAIR_bl.nii.gz ];
then
echo "Unzip those where followup may be run"
gunzip $folder/mFLAIR_fu.nii.gz
gunzip $folder/mFLAIR_bl.nii.gz
fi

if [ ! -f $folder/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz ] && [ ! -f $folder/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii ] && [ -f $folder/mFLAIR_bl.nii.gz ] && [ -f $folder/mFLAIR_fu.nii ];
then
echo "Unzip those where followup may be run"
#gunzip $folder/mFLAIR_fu.nii.gz
gunzip $folder/mFLAIR_bl.nii.gz
fi

done
