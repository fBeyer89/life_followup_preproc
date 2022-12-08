# Extract WML volume from lesion change maps

#run for all participants who have been copied to /data/pt_life_whm folder: N=2653
#extract either longitudinal lesion voxel numbers and volumes (here decrease, no change and increase are labeled by the numbers 1, 2, and 3, respectively)
# or
# extract lesion volume of binarized lesion_prob>0.8 cross-sectional mask for participants with one MRI only.

cd /data/pt_life_whm/Data/LST/

for subj in sub-110218055F #/data/pt_life_whm/Data/LST/sub*

do

echo $subj

gzip $subj/*.nii

if [ -f $subj/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz ];
then
echo "long"

expr1="`fslstats -K /data/pt_life_whm/Data/LST/$subj/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz /data/pt_life_whm/Data/LST/$subj/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz -V`"

echo $subj $expr1 >> /data/pt_life_whm/Results/Tables/longvols.txt

elif [ -f  $subj/ples_lpa_mFLAIR_bl.nii.gz && ! -f /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz ];
then

echo "only cross"

fslmaths /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl.nii.gz -thr 0.8 -bin /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz

expr2="`fslstats /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl.nii.gz -k /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz -V`"

elif [ -f  $subj/ples_lpa_mFLAIR_bl.nii.gz && -f /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz ];
then
expr2="`fslstats /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl.nii.gz -k /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz -V`"

echo $subj $expr2 >> /data/pt_life_whm/Results/Tables/cross_vols.txt

else
echo "none is available"

echo $subj 0 0 0 >> /data/pt_life_whm/Results/Tables/none.txt

fi

done

