#!/bin/bash

while read subj
do



if [ -d /data/p_life_raw/patients/${subj}/${subj}_2018*/PHYS_${subj}/${subj}/ ];
then

cd /data/p_life_raw/patients/${subj}/${subj}_2018*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /home/raid1/fbeyer/Documents/Scripts/LIFE_followup_QA/physio_preproc/overview.tsv

elif [ -d /data/p_life_raw/patients/${subj}/${subj}_2019*/PHYS_${subj}/${subj}/ ];
then
cd /data/p_life_raw/patients/${subj}/${subj}_2019*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /home/raid1/fbeyer/Documents/Scripts/LIFE_followup_QA/physio_preproc/overview.tsv

else

echo $subj 999 999 999 999 >> /home/raid1/fbeyer/Documents/Scripts/LIFE_followup_QA/physio_preproc/overview.tsv
fi

done < /data/p_life_raw/scripts/Followup/all_life_probands_26.02.19.txt
