library('haven')
library('lme4')

###
#CLEANING AND CHECKING THE NUMBERS
###

data=read.table("/home/raid1/fbeyer/Documents/Scripts/LIFE_followup_QA/physio_preproc/overview.tsv",fill = T)
colnames(data)=c("SIC","resp_rs", "pulse_rs", "resp_dti", "pulse_dti")

#all the ones who do not have a folder with physiological files:
data[data$resp_dti==999,]$SIC

#file size should be 154 for respiration and 240 for pulse (for RS)
##problems with respiratory file for resting-state (4)
data[data$resp_dti!=999&data$resp_rs<154,]$SIC #LI0003255X LI00640890 LI00461695 LI00958910

##problems with pulse file for resting-state (13)
data[data$resp_rs!=999&data$pulse_rs<240,]$SIC

##247 participants on 26.2.19
length(data$SIC)

##232 participants do have Physlogfiles on 26.2.19
length(data[data$resp_rs!=999,]$SIC)

##217 participants have (probably) useful Physlogfiles on 26.2.19
length(data[data$resp_rs!=999&data$pulse_rs==240&data$resp_rs==154,]$SIC)

############################################################################################################
##COMPARING HEAD MOTION AND PHYSIOLOGICAL FILES
data=read.table("/data/pt_life_restingstate_followup/results/results_rs_motion_physio.csv",header=T,fill = T,sep = ',')
SIC=read.table("/data/pt_life_restingstate_followup/results/SIC.csv",header=T,fill = T,sep = ',')
data$SIC=SIC$Var1
length(data$SIC)

##read baseline data and match
bl=read_sav('/afs/cbs.mpg.de/share/gr_agingandobesity/life_shared/LIFE_comprehensive_list/head_motion/LIFE_subjects_motion_params.sav')
bl=bl[,c("SIC","meanFD_new","mean_FD_P")]

widetable=merge(data,bl,by.x = "SIC")
##sanity check: mean FD (from python calculation) and mean FD (from new script) at baseline agree.

##exclude participants without resting state
##because of unfinished preprocessing or data from LIFE Update -> N=13
data[data$meanFD==0,"SIC"]
data=data[data$meanFD!=0,]
length(data$SIC)

#participants without DVARS -> only one doesn't have DVARS "LI0057625X, rerun?"
data[data$meanstdDVARS==0,"SIC"]
data=data[data$meanstdDVARS!=0,]
length(data$SIC)

##PLOT some histograms
par(mfrow=c(2,2))
hist(data$meanFD, main = "mean FD")
hist(data$maxFD, main = "max FD")
hist(data$meanstdDVARS, main = "mean DVARS")
hist(data$maxstdDVARS, main = "max DVARS")

#mean FD and DVARS are strongly correlated
par(mfrow=c(1,1))
hist(data$corr_FD_stdDVARS, main = "correlation betw. mean FD & DVARS")
t.test(data$corr_FD_stdDVARS)

#CORRELATION of motion and physiological parameters
par(mfrow=c(2,1))
hist(data$corr_FD_resp, main = "mean FD and downs. resp")
t.test(data$corr_FD_resp)
hist(data$corr_FD_oxy, main = "mean FD and downs. oxy")
t.test(data$corr_FD_oxy)

par(mfrow=c(2,1))
hist(data$corr_FD_RVT, main = "mean FD and RVT")
t.test(data$corr_FD_RVT)
hist(data$corr_FD_HR, main = "mean FD and HR")
t.test(data$corr_FD_HR)

#exploring some participants
data[data$corr_FD_HR>0.4,"SIC"]

#5 participants with "much" motion maxFD>3 or meanFD>0.5
#according to old criteria.
data[data$meanFD>0.5|data$maxFD>3,"SIC"]

#correlation of physio and motion only in high motion subjects -> also very small.
t.test(data[data$meanFD>0.2,]$corr_FD_RVT)
t.test(data[data$meanFD>0.2,]$corr_FD_HR)

###COMPARE BASELINE AND FOLLOWUP

#exclude everybody with meanFD=0 -> not preprocessed at BL
wide=data[data$meanFD_BL!=0,]


library(reshape2)

# Specify id.vars: the variables to keep but not split apart on
long = melt(wide, id.vars=c("SIC","meanstdDVARS", "maxstdDVARS","corr_FD_stdDVARS",
                                  "corr_FD_resp","corr_FD_oxy","corr_FD_RVT","corr_FD_HR",
                                  "maxFD","maxFD_BL"))

levels(long$variable)=c("fu","bl")
long$variable <- relevel(long$variable, "bl")
colnames(long)[12]="mean_FD"

#mean FD pre-post difference (difference/mean value)
library(ggplot2)

p <- ggplot(aes(x = variable, y=mean_FD),data=long)+ geom_violin() + geom_point()
p

tspag = ggplot(long, aes(x=variable, y=mean_FD,group=SIC)) + 
  geom_line(aes(color=SIC)) + guides(colour=TRUE)
tspag + theme(axis.text=element_text(size=10),axis.title=element_text(size=12),strip.text = element_text(size=12),legend.position="none")
names(vols_long_selected)

####STATISTICS
#get some covariates
cov<-read.table("/afs/cbs.mpg.de/share/gr_agingandobesity/life_shared/LIFE_comprehensive_list/PV168_A1_Pilot_subject_list_inclusion_exclusion29.1.19.csv", 
                header=T, sep=',')
cov=cov[,c("SIC","sex","Age_all","bmi")]
long_with_demo=merge(long,cov, by.x="SIC")

par(mfrow=c(1,1))
hist(long_with_demo$Age_all, main = "Age distribution")




##CROSSSECTIONAL ANALYSIS

res=lm (mean_FD ~ Age_all + as.factor(sex), data=long_with_demo[long_with_demo$variable=="bl",])
summary(res)

res=lm (mean_FD ~ Age_all + bmi + as.factor(sex), data=long_with_demo[long_with_demo$variable=="bl",])
summary(res)

res=lm (mean_FD ~ Age_all + as.factor(sex), data=long_with_demo[long_with_demo$variable=="fu",])
summary(res)

res=lm (mean_FD ~ Age_all + bmi + as.factor(sex), data=long_with_demo[long_with_demo$variable=="fu",])
summary(res)

##LONGITUDINAL ANALYSIS for motion
par(mfrow=c(1,1))
plot(long_with_demo$Age_all, long_with_demo$mean_FD, 
     col=as.numeric(long_with_demo$variable),
     main = "Age(BL) and mean FD @BL")
legend("topleft",legend = c("black:bl", "red:fu"))

plot(long_with_demo$bmi, long_with_demo$mean_FD, 
     col=as.numeric(long_with_demo$variable),
     main = "BMI(BL) and mean FD @BL")
legend("topleft",legend = c("black:bl", "red:fu"))

##MODEL 1

null<-lmer(mean_FD ~ (1|SIC), data=long_with_demo)
res1<-lmer(mean_FD ~ as.factor(variable) + (1|SIC), data=long_with_demo)

##there is a significant difference between timepoints
anova(res1,null)


#male and older people also move more
res2<-lmer(mean_FD ~ as.factor(sex) + Age_all + as.factor(variable) + (1|SIC), data=long_with_demo)


res3<-lmer(mean_FD ~ as.factor(sex) + Age_all + bmi + as.factor(variable) + (1|SIC), data=long_with_demo)
summary(res3)

##LONGITUDINAL ANALYSIS for physiodata
##people with higher BMI take deeper breaths.
res=lm(corr_FD_RVT~bmi + as.factor(sex) + Age_all , data=widetable)

##test
install.packages('dataMaid')
library(dataMaid)

makeCodebook(data)
makeCodebook(cov)

