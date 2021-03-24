@author: imruizhang

## useful commands
- to see the current status of the files that needed to be commit, push or add...
`git status`
- to view branches
`git branch`
the current branch will be highline with an asterisk
- to switch branches
`git checkout 'branch-name'`
### Note: branch is quite complicated, not very sure how it works.
- What I knew so far:
	- the changes within the branch would not affect the master branch, but you may need to remove the files when you use `git rm --cached 'file name'` within the branch, otherwise you cannot switch back to master.
	- when you use `git push origin 'branch-name'`, your changes are only visible under the branch not on the master level.

## before uploading changes to github

`git commit -a -m 'what-has-changed'` or `git commit 'file-name' -m 'what-has-changed'` if you want to comment the changes differently for each file.
if you forgot to use `-m 'comments'`, you will open a commit text editor in your terminal, type your comments and ^KX to save and exit (^KH for help).

## to upload changes to github if the changes were made in a branch
- switch to the master branch
`git checkout master`
- pull the changes in case other members changed something (optional)
`git pull origin master`
- merge the changes from your branch
`git merge 'branch-name'`
- push the chagnes to github
`git push origin master`

## Updating your fork from original repo to keep up with their changes
- Add remote from original repository in your forked repository (only need to do it once):
`git remote add upstream git://github.com/ORIGINAL-DEV-USERNAME/REPO-YOU-FORKED-FROM.git`
- Usuall update
`git fetch upstream`
`git pull upstream master`

## how to delete files from git when they were added to .gitignore later
git rm --cached `git ls-files -i --exclude-from=.gitignore`
git commit -m 'Removed all files that are in the .gitignore'
git push origin master
