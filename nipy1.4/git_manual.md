@author: imruizhang

## Using the Fork-and-Branch
### Before doing any changes

- Fork a GitHub repository: log into your account; find the repository; click 'Fork' botton.
- Make a local clone: `git clone https://github.com/YOUR-USERNAME/REPO-YOU-FORKED.git`
- - Add remote from original repository in your forked repository: `git remote add upstream https://github.com/ORIGINAL-DEV-USERNAME/REPO-YOU-FORKED-FROM.git`, `git fetch upstream`
- Create a new branch: `git checkout -b NEW-BRANCH-NAME` (now you switch to this new branch)

### After making changes

- Commit changes: `git commit -a -m YOUR-CHANGES` to give the same commit to all files or `git commit FILE-NAME -m YOURCHANGES` if you want to comment the changes differently for each file. Note if you forgot to use `-m YOURCHANGES`, you will open a commit text editor in your terminal, type your comments and ^KX to save and exit (^KH for help).
- Push changes: `git push origin YOUR-BRANCH-NAME`
- Open a pull request (from the browser)
- Owner of the repository aprove the pull request

**Important Note: use branches to push your changes, do not push to the master branch**
Branch is quite complicated, what I knew so far:
- the changes within the branch would not affect the master branch, but you may need to remove the files when you use `git rm --cached 'file name'` within the branch, otherwise you cannot switch back to master.
- when you use `git push origin 'branch-name'`, your changes are only visible under the branch not on the master level.

> **As a general rule of thumb, you should limit a branch to one logical change. The definition of one logical change will vary from project to project and developer to developer, but the basic idea is that you should only make the necessary changes to implement one specific feature or enhancement.**


### Clean up after a merged pull request
- Updating your local copy from original repo to keep up with their changes: `git pull upstream master`
- Delete the feature branch in which chages have been updated `git branch -d BRANCH-NAME`
- Update the master branch in your forked repository `git push origin master`
- (TODO:testing) Push the deletion of the branch to your GitHub: `git push --delete origin BRANCH-NAME`

## Some useful commands
- to see the current status of the files that needed to be commit, push or add...
`git status`
- to view branches
`git branch`
the current branch will be highline with an asterisk
- to switch branches
`git checkout 'branch-name'`
- switch to the master branch
`git checkout master`
- pull the changes from the master
`git pull origin master`
- merge the changes from your branch
`git merge 'branch-name'`
- push the chagnes to github
`git push origin master`

## how to delete files from git when they were added to .gitignore later
git rm --cached `git ls-files -i --exclude-from=.gitignore`
git commit -m 'Removed all files that are in the .gitignore'
git push origin master
