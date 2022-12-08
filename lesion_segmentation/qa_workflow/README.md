# QA workflow

Workflow to create PDF plot of FLAIR image overlaid with LCL change maps.

## To run
- getserver -sL
- start FSL --version 5.0.11
- start a python3 environment including nipype [miniconda, source activate py3]
- update subject list in `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/qa_workflow/run_python_3.txt`
- run the script by typing `run base_reports.py`
