for subj in  sub-25F8C1CF3C sub-4213544E08 sub-A8A6D338E1 sub-980D7F1B46 sub-E738D58064 sub-43F7100A14 sub-B687779C12 sub-E134854A4F sub-3173B5B579 sub-9B2B6BC54C sub-FD77D1769B sub-FADB02A98A sub-74A8D1F7CB sub-A1278A222B sub-2989DF8D49 sub-4ED46EC3FF sub-E3AC41E17E sub-BA42AAEFDC sub-82CDD7A624 sub-15E7897CDD 

do 

gunzip /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl.nii.gz
gunzip /data/pt_life_whm/Data/LST/$subj/mFLAIR_bl.nii.gz

rm -rf /data/pt_life_whm/Data/LST/$subj/ples_lpa_mFLAIR_bl_thr0.8_bin.nii.gz

if [ -f /data/pt_life_whm/Data/LST/$subj/FLAIR_fu.nii ];
then
gzip /data/pt_life_whm/Data/LST/$subj/FLAIR_fu.nii
fi

done
