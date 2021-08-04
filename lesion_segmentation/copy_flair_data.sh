#copy LIFE FLAIR scans from baseline and followup to working directory

cd /data/p_life_raw/bids

wd="/data/pt_life_whm/Data/LST/"
mkdir -p $wd

#test subjects: sub-A0038A0EFA sub-C12CCEE126 sub-DF34687255

for subj in sub-25F8C1CF3C sub-4213544E08 sub-A8A6D338E1 sub-980D7F1B46 sub-E738D58064 sub-15E7897CDD sub-43F7100A14 sub-B687779C12 sub-E134854A4F sub-3173B5B579 sub-9B2B6BC54C sub-FD77D1769B sub-FADB02A98A sub-74A8D1F7CB sub-A1278A222B sub-2989DF8D49 sub-4ED46EC3FF sub-E3AC41E17E sub-BA42AAEFDC sub-82CDD7A624 #`ls -d sub-*`
do 
for tp in fu
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
