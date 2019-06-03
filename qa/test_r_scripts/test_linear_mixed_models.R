library(haven)
library(reshape2)
library(ggplot2)

source('/afs/cbs.mpg.de/share/gr_agingandobesity/literature/original_articles/statistics/linear_models_course/course_scripts/own_functions/plot_diagnostics.R')
source('/afs/cbs.mpg.de/share/gr_agingandobesity/literature/original_articles/statistics/linear_models_course/course_scripts/own_functions/diagnostics_dfbeta_cooks.R')
source('/a/share/gr_agingandobesity/literature/methods/statistics/linear_models_course_rogermundry_2018/functions/glmm_stability.r')

#demographics from baseline
cov<-read.table("/afs/cbs.mpg.de/share/gr_agingandobesity/life_shared/LIFE_comprehensive_list/PV168_A1_Pilot_subject_list_inclusion_exclusion29.1.19.csv", 
                header=T, sep=',')
cov=cov[,c("SIC","sex","Age_all","bmi")]

rsphysio=read.table("/data/pt_life_restingstate_followup/results/results_rs_motion_physio.csv",header=T,fill = T,sep = ',')
SIC=read.table("/data/pt_life_restingstate_followup/results/SIC.csv",header=T,fill = T,sep = ',')
rsphysio$SIC=SIC$Var1

##read baseline data and match
bl=read_sav('/afs/cbs.mpg.de/share/gr_agingandobesity/life_shared/LIFE_comprehensive_list/head_motion/LIFE_subjects_motion_params.sav')
bl=bl[,c("SIC","meanFD_new","maxFD_new")]

widetable=merge(rsphysio,bl,by.x = "SIC")

##exclude participants without resting state
##because of unfinished preprocessing or data from LIFE Update -> N=13
rsphysio=rsphysio[rsphysio$meanFD!=0,]

#participants without DVARS -> only one doesn't have DVARS "LI0057625X, rerun?"
rsphysio[rsphysio$meanstdDVARS==0,"SIC"]
rsphysio=rsphysio[rsphysio$meanstdDVARS!=0,]
length(rsphysio$SIC)

##Head motion compared with baseline assessment
###Cross-sectional analysis
#exclude everybody with meanFD=0 -> not preprocessed at BL
wide=rsphysio[rsphysio$meanFD_BL!=0&rsphysio$meanFD!=0,]
wide_with_demo=merge(wide,cov, by.x="SIC")

# Specify id.vars: the variables to keep but not split apart on
long = melt(wide, id.vars=c("SIC","meanstdDVARS", "maxstdDVARS","corr_FD_stdDVARS",
"corr_FD_resp","corr_FD_oxy","corr_FD_RVT","corr_FD_HR",
"corr_dvars_resp","corr_dvars_oxy","corr_dvars_RVT","corr_dvars_HR",
"maxFD","maxFD_BL"))

levels(long$variable)=c("fu","bl")
long$variable <- relevel(long$variable, "bl")
colnames(long)[16]="mean_FD"
colnames(long)[15]="timepoint"

long_with_demo=merge(long,cov, by.x="SIC")
long_with_demo$Age_all_z=scale(long_with_demo$Age_all)
long_with_demo$sex_z=scale(as.numeric(long_with_demo$sex))

###Longitudinal analysis
p <- ggplot(aes(x = timepoint, y=mean_FD),data=long)+ geom_violin() + geom_point()
p

tspag = ggplot(long, aes(x=timepoint, y=mean_FD,group=SIC)) + 
geom_line(aes(color=SIC)) + guides(colour=TRUE)
tspag + theme(axis.text=element_text(size=10),axis.title=element_text(size=12),strip.text = element_text(size=12),legend.position="none")

##LONGITUDINAL ANALYSIS for motion
library(lme4)
##MODEL 1
long_with_demo$tp=as.factor(long_with_demo$timepoint)

null<-lmer(mean_FD ~ (1|SIC), data=long_with_demo,  REML=F)
summary(null)
res1<-lmer(mean_FD ~ tp + (1|SIC), data=long_with_demo, REML=F)
summary(res1)

#testing assumptions
ranef.diagn.plot(res1)#normal distribution of random effects
diagnostics.plot(res1)#normal distribution of residuals..

contr=lmerControl(optCtrl=list(maxfun=100000))
m.stab=glmm.model.stab(model.res=res1, contr=contr)#model stability
m.stab$detailed$warnings #no warnings

summary(res1)
drop1(res1, test="Chisq")

##there is a significant difference between timepoints
res_tp=anova(res1,null,test="Chisq")
res_tp
p_tp=res_tp$`Pr(>Chisq)`[2]

##simulate change in BMI predicts change in FD

#average BMI change:
mean(wide_with_demo$meanFD-wide_with_demo$meanFD_BL)
range((wide_with_demo$meanFD-wide_with_demo$meanFD_BL))
std=2#error/imprecision of BMI change.

#either followup BMI is unrelated to mean FD ("trait") : Case1
#wide_with_demo$bmi_fu=wide_with_demo$bmi+ rnorm(length(wide_with_demo$bmi), mean = 0, sd = std)

#either mean FD changes relate to followup BMI changes ("state"): Case2
wide_with_demo$bmi_fu=wide_with_demo$bmi+
  2*(wide_with_demo$meanFD-wide_with_demo$meanFD_BL)+
  rnorm(length(wide_with_demo$meanFD), mean = 0, sd = std)

long_sim = melt(wide_with_demo, id.vars=c("SIC","meanstdDVARS", "maxstdDVARS","corr_FD_stdDVARS",
                            "corr_FD_resp","corr_FD_oxy","corr_FD_RVT","corr_FD_HR",
                            "corr_dvars_resp","corr_dvars_oxy","corr_dvars_RVT","corr_dvars_HR",
                            "maxFD","maxFD_BL", "Age_all", "sex"))

#cut all followup - baseline timepoints
long_sim_cut=long_sim[1:448,]

levels(long_sim$variable)

#place holder variable
long_sim_cut[1:448,"bmi"]=long_sim_cut$Age_all

#followup BMI
levels(droplevels(long_sim[673:896,]$variable))
long_sim_cut[1:224,]$bmi=long_sim[673:896,]$value
#baseline BMI
levels(droplevels(long_sim[225:448,]$variable))
long_sim_cut[225:448,]$bmi=long_sim[449:672,]$value

colnames(long_sim_cut)[18]="meanFD"
colnames(long_sim_cut)[17]="timepoint"

long_sim_cut$timepoint=droplevels(long_sim_cut$timepoint)
levels(long_sim_cut$timepoint)=c("fu","bl")
long_sim_cut$timepoint <- relevel(long_sim_cut$timepoint, "bl")

##checking BMI change
tspag = ggplot(long_sim_cut, aes(x=timepoint, y=bmi, group=SIC)) + 
  geom_line(aes(color=SIC)) + guides(colour=TRUE)
tspag + theme(axis.text=element_text(size=10),axis.title=element_text(size=12),strip.text = element_text(size=12),legend.position="none")


##a model using BMI to predict mean FD change
null<-lmer(meanFD ~ (1|SIC), data=long_sim_cut,  REML=F)
summary(null)
res1<-lmer(meanFD ~ bmi + (1|SIC), data=long_sim_cut, REML=F)
summary(res1)
anova(res1,null)

tspag = ggplot(long_sim_cut, aes(x=bmi, y=meanFD,group=SIC)) + 
  geom_line(aes(color=SIC)) + geom_point(aes(shape=timepoint))
#+  guides(colour=TRUE)
tspag + theme(axis.text=element_text(size=10),axis.title=element_text(size=12),strip.text = element_text(size=12),legend.position="none")

##maybe not exactly right. Use rogers example to tease apart between/within subjects

#mean BMI in subject
mean.bmi.p.subj=tapply(X=long_sim_cut$bmi,
                      INDEX=long_sim_cut$SIC, FUN=mean)
long_sim_cut$mean.bmi.p.subj=
  mean.bmi.p.subj[as.numeric(long_sim_cut$SIC)]

#variation in BMI within subject (+/- difference to mean)
long_sim_cut$within.bmi.p.subj=
  long_sim_cut$bmi-long_sim_cut$mean.bmi.p.subj

tapply(X=long_sim_cut$within.bmi.p.subj, INDEX=long_sim_cut$SIC,
       FUN=mean)

#not possible to model random effects of within-subject slope (only 2 measurements)
res=lmer(meanFD ~  mean.bmi.p.subj + within.bmi.p.subj + (1 |SIC),
         data=long_sim_cut, REML=F)

#diagnostics and convergence
diagnostics.plot(res)
ranef.diagn.plot(res)
#m.stab=glmm.model.stab(model.res = res)
#to check whether there were any converge issues:
table(m.stab$detailed$warnings)
m.stab$summary

#null model. significant effect of ind. variation in BMI
null=lmer(meanFD ~  mean.bmi.p.subj + (1 |SIC),
          data=long_sim_cut, REML=F)#the intercept is included by default. If you want to exclude it you would do R ~ 0 + ...

as.data.frame(anova(res,null,test="Chisq"))

#Case1:
#if BMI and MD change are completely independent, than the between subject effect is not significant.
#MD is a trait which does not change significantly with BMI (when BMI is altered).

#Case2:
#if BMI changes are related to MD changes, there is a significant within-subject effect of BMI.
#state-like relation



##how to relate behavioral traits..