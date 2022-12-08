#copy LIFE FLAIR scans from baseline and followup to working directory
#bl refers to first scan of the participant (14 pilot and main participants are thus included with their first measurement)

cd /data/p_life_raw/bids

wd="/data/pt_life_whm/Data/LST/"
mkdir -p $wd

#test subjects: sub-A0038A0EFA sub-C12CCEE126 sub-DF34687255

for subj in sub-63D31D6C5D sub-7518497768 sub-D3F3921BEE sub-C15A19C13C sub-1C091C313C sub-2E53F0E601 sub-982AAD8304 sub-D593494506 sub-1F861C7B0F sub-10F692D5C2 sub-3C2A21C6F3 sub-44F328348E sub-5A9AA93753 sub-EB7CA9564F sub-467E0799FF sub-EBFABDDF77 sub-D7EB919BFA
 #`ls -d sub-*`
do 

gunzip $wd/$subj/FLAIR_bl.nii.gz
rm -rf $wd/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz
gunzip $wd/$subj/ples_lpa_mFLAIR_bl.nii.gz
gunzip $wd/$subj/mFLAIR_bl.nii.gz

for tp in bl fu
do
echo "Subject: $subj at timepoint $tp"

if [ -f $subj/ses-$tp/anat/*_FLAIR.nii.gz ] && [ ! -f $wd/$subj/FLAIR_$tp.nii.gz ] && [ ! -f $wd/$subj/FLAIR_$tp.nii ];
then 
#mkdir $wd/$subj/
cp $subj/ses-$tp/anat/*_FLAIR.nii.gz $wd/$subj/FLAIR_$tp.nii.gz

if [ ! -f $wd/$subj/FLAIR_$tp.nii ];
then
gunzip $wd/$subj/FLAIR_$tp.nii.gz
else
echo "already unzipped"
fi

else 
echo "not acquired or already converted"
fi




#if [ -f $wd/$subj/FLAIR_bl.nii ] && [ -f $wd/$subj/FLAIR_fu.nii ];
#then 
#echo $subj >> /data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/long_subjects.txt
#fi

done
done
