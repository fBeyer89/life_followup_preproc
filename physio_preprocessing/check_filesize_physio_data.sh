#!/bin/bash
rm -rf /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt

while read subj
do

echo $subj

if [ -d /data/p_life_raw/patients/${subj}/${subj}_2018*/PHYS_${subj}/${subj}/ ];
then

cd /data/p_life_raw/patients/${subj}/${subj}_2018*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt

elif [ -d /data/p_life_raw/patients/${subj}/${subj}_2019*/PHYS_${subj}/${subj}/ ];
then
cd /data/p_life_raw/patients/${subj}/${subj}_2019*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt

elif [ -d /data/p_life_raw/patients/${subj}/${subj}_2020*/PHYS_${subj}/${subj}/ ];
then
cd /data/p_life_raw/patients/${subj}/${subj}_2020*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt

elif [ -d /data/p_life_raw/patients/${subj}/${subj}_2021*/PHYS_${subj}/${subj}/ ];
then
cd /data/p_life_raw/patients/${subj}/${subj}_2021*/PHYS_${subj}/${subj}/

file_size_resp=`du -k *.resp | cut -f1`
file_size_cardiac=`du -k *.puls | cut -f1`

echo $subj $file_size_cardiac $file_size_resp >> /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt


else

echo $subj 999 999 999 999 >> /data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/overview_filesize.txt
fi

done < /data/p_life_raw/scripts/Followup/check_overview/all_life_scans_2021.txt
