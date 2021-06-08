#copy LIFE FLAIR scans from baseline and followup to working directory

cd /data/p_life_raw/bids

wd="/data/pt_life/LIFE_fu/lesionsegmentation/"
#test subjects: sub-A0038A0EFA sub-C12CCEE126 sub-DF34687255

for subj in sub-305DAA97CA sub-6B29406750 sub-3A8A05B5BD #`ls -d sub-*`
do 
for tp in bl fu
do


if [ -f $subj/ses-$tp/anat/*_FLAIR.nii.gz ];
then 
mkdir $wd/$subj/
cp $subj/ses-$tp/anat/*_FLAIR.nii.gz $wd/$subj/FLAIR_$tp.nii.gz
gunzip $wd/$subj/FLAIR_$tp.nii.gz
else 
echo "not acquired"
fi


if [ -f $wd/$subj/FLAIR_bl.nii && $wd/$subj/FLAIR_fu.nii ];
then 
echo $subj >> /data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/long_subjects.txt
fi

done
done
