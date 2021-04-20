# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:08:45 2019

@author: fbeyer
"""


def juggle_subj(subject, bids_outputdir):
    import pandas as pd
    from datetime import datetime as dt
    import os
    import random, string

    sic_pseudo=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/pseudo_mrt_20201214.csv")
    tmp=sic_pseudo.loc[sic_pseudo.sic == subject,'pseudonym']
    if len(tmp.get_values()) == 0:
        print "no pseudonym found"
        pseudo = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        print pseudo
        tmp = pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/lifebids/new_pseudos.csv")
        tmp = tmp.append({"sic":subject, "pseudo": pseudo}, ignore_index=True)
        print tmp
        tmp.to_csv("/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/lifebids/new_pseudos.csv")
    else:
        pseudo = tmp.get_values()[0]

    tp = "fu"
    if os.path.isdir('%ssub-%s/ses-%s' %(bids_outputdir,pseudo,tp)):
        tp = "fu2"

    return pseudo,tp


def create_bids(dicom_info, bids_info, bids_outputdir, subj, bvals, bvecs):
    import os
    import shutil
    import re
    import json

    rs_acq=None

    bids_outputs=[]

    [pseudo,ses]=juggle_subj(subj,bids_outputdir)

    #print dicom_info
    if not (os.path.isdir('%ssub-%s/ses-%s' %(bids_outputdir,pseudo,ses))):
        os.makedirs('%ssub-%s/ses-%s' %(bids_outputdir,pseudo,ses))

    #create necessary folders.
    if not (os.path.isdir('%ssub-%s/ses-%s/anat' %(bids_outputdir,pseudo,ses))):
        os.mkdir('%ssub-%s/ses-%s/anat' %(bids_outputdir,pseudo,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/func' %(bids_outputdir,pseudo,ses))):
        os.mkdir('%ssub-%s/ses-%s/func' %(bids_outputdir,pseudo,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/dwi' %(bids_outputdir,pseudo,ses))):
        os.mkdir('%ssub-%s/ses-%s/dwi' %(bids_outputdir,pseudo,ses))
    if not (os.path.isdir('%ssub-%s/ses-%s/fmap' %(bids_outputdir,pseudo,ses))):
        os.mkdir('%ssub-%s/ses-%s/fmap' %(bids_outputdir,pseudo,ses))

    for sm in dicom_info:

        if sm['protocol_name']== None:
            continue
        #################### anatomical imaging ################################
        if sm['protocol_name']=="t2_spc_da-fl_irprep_sag_p2_iso":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_FLAIR.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_FLAIR.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            bids_outputs.append("FLAIR")

        elif sm['protocol_name']=="MPRAGE_MPIL":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-MPIL_T1w.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-MPIL_T1w.json' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bids_outputs.append("MPRAGE_MPIL")

        elif sm['protocol_name']=="MPRAGE_MPIL_32Ch":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-MPIL32Ch_T1w.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-MPIL32Ch_T1w.json' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bids_outputs.append("MPRAGE_MPIL_32Ch")

        elif sm['protocol_name']=="MPRAGE_ADNI":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI_T1w.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI_T1w.json' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bids_outputs.append("MPRAGE_ADNI")

        elif sm['protocol_name']=="MPRAGE_ADNI_32Ch_PAT2":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI32ChPAT2_T1w.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI32ChPAT2_T1w.json' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bids_outputs.append("MPRAGE_ADNI_32Ch_PAT2")

        elif sm['protocol_name']=="MPRAGE_ADNI_32Ch":
            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI32Ch_T1w.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ADNI32Ch_T1w.json' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bids_outputs.append("MPRAGE_ADNI_32Ch")

        #################### field map for resting-state ################################
        elif sm['series_desc']=="gre_field_mapping" and sm['image_type'][2]=='M':

            print "gre_field_mapping"
            #find list element from json
            r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'],'%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_magnitude1.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            fname='%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.json' %(bids_outputdir,pseudo,ses,pseudo,ses)
            shutil.copyfile(sel_json[0], fname)

            with open(fname, 'r') as f:
                data = json.load(f)
                if sm.has_key('echo_times'):
                    data['EchoTime1']=sm['echo_times'][0]*0.001
                    data['EchoTime2']=sm['echo_times'][1]*0.001
                elif sm.has_key('echo_time'):
                    print "has only one echo time (older version of scanner software maybe)"
                    data['EchoTime1']=(sm['echo_time']-2.46)*0.001
                    data['EchoTime2']=sm['echo_time']*0.001
                else:
                    "no echo time found for this fieldmap"
                if isinstance(rs_acq, str):
                    data["IntendedFor"] = rs_acq
                f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

            bids_outputs.append("gre_field_mapping")
        elif sm['series_desc']=="gre_field_mapping" and sm['image_type'][2]=='P':
            #find list element from json
            r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'],'%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))

        elif sm['series_desc']=="cmrr_mbep2d_resting":

            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-cmrr_bold.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-cmrr_bold.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            fname='%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-cmrr_bold.json' %(bids_outputdir,pseudo,ses,pseudo,ses)
            with open(fname, 'r') as f:
                data = json.load(f)
                #print data
                data['TaskName']='rest'

            f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

            rs_acq ='ses-%s/func/sub-%s_ses-%s_task-rest_acq-cmrr_bold.nii.gz' %(ses,pseudo,ses)
            fname = '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.json' % (bids_outputdir, pseudo, ses, pseudo, ses)
            if os.path.isfile(fname):
                with open(fname, 'r') as f:
                    data = json.load(f)
                    # print data
                    data['IntendedFor'] = rs_acq

                f.close()
                with open(fname, 'w') as f:
                    json.dump(data, f)

            bids_outputs.append("cmrr_mbep2d_resting")

        #################### resting-state ################################
        elif sm['series_desc']=="t2star_epi_2D_standard":

            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-standard_bold.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-standard_bold.json' %(bids_outputdir,pseudo,ses,pseudo,ses))


            fname='%ssub-%s/ses-%s/func/sub-%s_ses-%s_task-rest_acq-standard_bold.json' %(bids_outputdir,pseudo,ses,pseudo,ses)
            with open(fname, 'r') as f:
                data = json.load(f)
                #print data
                data['TaskName']='rest'
            f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

            rs_acq = 'ses-%s/func/sub-%s_ses-%s_task-rest_acq-standard_bold.nii.gz' %(ses,pseudo,ses)
            fname = '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-rs_phasediff.json' % (
            bids_outputdir, pseudo, ses, pseudo, ses)
            if os.path.isfile(fname):
                with open(fname, 'r') as f:
                    data = json.load(f)
                    # print data
                    data['IntendedFor'] = rs_acq

                f.close()
                with open(fname, 'w') as f:
                    json.dump(data, f)

            bids_outputs.append("t2star_epi_2D_standard")

        #################### field map for diffusion ################################
        elif sm['series_desc']=="cmrr_mbep2d_se_AP_unwarp_diff":
            r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))


            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-norm_epi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-norm_epi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            fname='%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-norm_epi.json' %(bids_outputdir,pseudo,ses,pseudo,ses)

            with open(fname, 'r') as f:
                data = json.load(f)
                #print data
                data['IntendedFor']='ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.nii.gz' %(ses,pseudo,ses)

            f.close()
            with open(fname, 'w') as f:
                json.dump(data, f)

            bids_outputs.append("cmrr_mbep2d_diff_unwarp")

        elif sm['series_desc']=="cmrr_mbep2d_se_PA_unwarp_diff":

                r = re.compile('.*%s_s%s.*.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))


                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-invpol_epi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-invpol_epi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                fname='%ssub-%s/ses-%s/fmap/sub-%s_ses-%s_acq-dwi_dir-invpol_epi.json' %(bids_outputdir,pseudo,ses,pseudo,ses)
                with open(fname, 'r') as f:
                    data = json.load(f)
                    #print data
                    data['IntendedFor']='ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.nii.gz' %(ses,pseudo,ses)

                f.close()
                with open(fname, 'w') as f:
                    json.dump(data, f)

        ################ diffusion-weighted imaging ################
        elif sm['series_desc']=="MPIL_DTI_100":

            # find list element from json
            r = re.compile('.*%s_s%s.json' % (sm['protocol_name'], sm['series_num']))
            sel_json = list(filter(r.match, bids_info))
            dirname = os.path.dirname(sel_json[0])
            bvec_name='%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num'])

            if os.path.isfile(bvec_name):
                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil100_dwi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil100_dwi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                #copy bval/bvec
                #get dir name of bval/bvex

                shutil.copyfile('%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil100_dwi.bvec' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile('%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil100_dwi.bval' %(bids_outputdir,pseudo,ses,pseudo,ses))
                bids_outputs.append("MPIL_DTI100")
            else:
                print("Error: DTI has no bvec")
                continue

        elif sm['series_desc']=="MPIL_DTI":

            # find list element from json
            r = re.compile('.*%s_s%s.json' % (sm['protocol_name'], sm['series_num']))
            sel_json = list(filter(r.match, bids_info))
            dirname = os.path.dirname(sel_json[0])
            bvec_name='%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num'])

            if os.path.isfile(bvec_name):

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil_dwi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil_dwi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                #copy bval/bvec

                shutil.copyfile('%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil_dwi.bvec' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile('%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-mpil_dwi.bval' %(bids_outputdir,pseudo,ses,pseudo,ses))
                bval_file='%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num'])
                bvec_file='%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num'])
                bids_outputs.append("MPIL_DTI")
            else:
                print("Error: DTI has no bvec")
                continue

        elif sm['series_desc']== "cmrr_mbep2d_diff":

            #find list element from json
            r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
            sel_json=list(filter(r.match,bids_info))

            shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            #copy bval/bvec
            #get dir name of bval/bvex
            dirname=os.path.dirname(sel_json[0])
            shutil.copyfile('%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.bvec' %(bids_outputdir,pseudo,ses,pseudo,ses))
            shutil.copyfile('%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num']), '%ssub-%s/ses-%s/dwi/sub-%s_ses-%s_acq-cmrr_dwi.bval' %(bids_outputdir,pseudo,ses,pseudo,ses))
            bval_file='%s/%s_s%s.bval' %(dirname,sm['protocol_name'],sm['series_num'])
            bvec_file='%s/%s_s%s.bvec' %(dirname,sm['protocol_name'],sm['series_num'])

            bids_outputs.append("cmrr_mbep2d_diff")

        ################ TOF angiography ################

        elif sm['protocol_name']=="tof_fl3d_tra":
            if sm['series_desc']=="tof_fl3d_tra":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_angio.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_angio.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                bids_outputs.append("tof_fl3d_tra")

            elif sm['series_desc']=="tof_fl3d_tra_MIP_SAG":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mipsag_angio.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mipsag_angio.json' %(bids_outputdir,pseudo,ses,pseudo,ses))


            elif sm['series_desc']=="tof_fl3d_tra_MIP_COR":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mipcor_angio.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mipcor_angio.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            elif sm['series_desc']=="tof_fl3d_tra_MIP_TRA":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-miptra_angio.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-miptra_angio.json' %(bids_outputdir,pseudo,ses,pseudo,ses))


        ################ SWI imaging ################
        elif sm['protocol_name']=="t2_fl3d_tra_p2_swi_highres_Siemens":
            if sm['series_desc']=="SWI_Images":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_swi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_swi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                bids_outputs.append("t2_fl3d_tra_p2_swi_highres_Siemens")
            elif sm['series_desc']=="mIP_Images(SW)":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mip_swi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mip_swi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            elif sm['series_desc']=="Mag_Images":
                #find list element from json
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mag_swi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-mag_swi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

            elif sm['series_desc']=="Pha_Images":
                #find list element from json
                r = re.compile('.*%s_s%s_ph.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ph_swi.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_acq-ph_swi.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

        ################ t2* flash imaging ################
        elif sm["protocol_name"]=="t2star_flash_2D_tra":
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_T2star.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/anat/sub-%s_ses-%s_T2star.json' %(bids_outputdir,pseudo,ses,pseudo,ses))

                bids_outputs.append("t2star_flash_2D_tra")

        ################ abdominal imaging ################
        elif ("t1_tse_trans" in sm["protocol_name"]):

                if not (os.path.isdir('%ssub-%s/ses-%s/abdomen' %(bids_outputdir,pseudo,ses))):
                    os.makedirs('%ssub-%s/ses-%s/abdomen' %(bids_outputdir,pseudo,ses))
                r = re.compile('.*%s_s%s.json' %(sm['protocol_name'],sm['series_num']))
                sel_json=list(filter(r.match,bids_info))

                shutil.copyfile(sm['nifti_file'], '%ssub-%s/ses-%s/abdomen/sub-%s_ses-%s_%s.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses,sm['protocol_name']))
                shutil.copyfile(sel_json[0], '%ssub-%s/ses-%s/abdomen/sub-%s_ses-%s_%s.nii.gz' %(bids_outputdir,pseudo,ses,pseudo,ses,sm['protocol_name']))

                bids_outputs.append("t1_tse_trans_mbh_pos")

        else:

                print "Series %s of Protocol %s could not be matched" %(sm['series_desc'], sm["protocol_name"])
    #print bids_outputs
    return bids_outputs, pseudo
