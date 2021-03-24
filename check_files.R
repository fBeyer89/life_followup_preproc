
table=read.table("/data/p_life_raw/scripts/Followup/compare_list.txt")
table$table=1

folder=read.table("/data/p_life_raw/scripts/Followup/life_FU_done_2020_11_10_08_29_37.txt")
folder$folder=1

all=merge(table, folder, by="V1", all=TRUE)

acq2020=read.table("/data/p_life_raw/scripts/Followup/acq2020.txt")
colnames(acq2020)=c("data","delimiter")
acq2020$V1=strsplit(toString(acq2020[,"data"]), "/")[[1]][seq(5,nrow(acq2020)*5,5)]

mergemiss=merge(acq2020, all, by="V1", all.x=TRUE)

mergemiss[is.na(mergemiss$table),]
