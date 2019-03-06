#install.packages('XLConnect')
library(XLConnect)
life_overview_02_2019<-readWorksheet(loadWorkbook("/data/p_life_raw/documents/MST/20190220_Übersicht_Untersuchungen MST.xlsx"),sheet=1)


exclusion_reasons=(life_overview_02_2019[life_overview_02_2019$MRT=="nein","wenn.nein..Grund"])

#16 due to metall
excl_metall <- life_overview_02_2019[grep("Metall", life_overview_02_2019$wenn.nein..Grund),]

#3 due to tinnitus + 2 due to linse
excl_tinnitus <- life_overview_02_2019[grep("Tinnitus", life_overview_02_2019$wenn.nein..Grund),] 
exl_linse <- life_overview_02_2019[grep("Linse", life_overview_02_2019$wenn.nein..Grund),] 

#14 due to operation + 9 due to stents + 4 künstl. hüfte + 3 herzschrittmacher + 3 retainer
excl_OP <- life_overview_02_2019[grep("OP", life_overview_02_2019$wenn.nein..Grund),] 
excl_operation <- life_overview_02_2019[grep("Operation", life_overview_02_2019$wenn.nein..Grund),] 
excl_ops <- life_overview_02_2019[grep("KI: Ops", life_overview_02_2019$wenn.nein..Grund),] 
excl_stents <- life_overview_02_2019[grep("Stent", life_overview_02_2019$wenn.nein..Grund),] 
excl_hüfte <- life_overview_02_2019[grep("Hüfte", life_overview_02_2019$wenn.nein..Grund),] 
excl_herzs <- life_overview_02_2019[grep("Herz", life_overview_02_2019$wenn.nein..Grund),] 
excl_retainer <- life_overview_02_2019[grep("Retainer", life_overview_02_2019$wenn.nein..Grund),] 

#10 due to platzangst
excl_platzangst <- life_overview_02_2019[grep("angst", life_overview_02_2019$wenn.nein..Grund),] 

#7 (??) + 9 unknown
excl_unknown <- life_overview_02_2019[grep("freigegeben", life_overview_02_2019$wenn.nein..Grund),] 

#3 tattoo or permanent makeup
excl_tattoo <- life_overview_02_2019[grep("Tattoo", life_overview_02_2019$wenn.nein..Grund),] 
excl_perm <- life_overview_02_2019[grep("Make", life_overview_02_2019$wenn.nein..Grund),] 

