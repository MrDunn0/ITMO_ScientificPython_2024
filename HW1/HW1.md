# **Homework 1: Git**
**Author**: Mikhail Ushakov

# Part 2
After creation and clonning of the repository I created the HW1 directory with all related files.


1-4. Create HW1 branch, add necessary files and push them to the repo:

```
git branch HW1
git checkout HW1
git add HW1
git commit -m "Add HW1 initial files"
git push --set-upstream origin HW1
```

5. Create branch "testing"

```
git branch testing
```

6-7. Add changes to the "hw1.txt" in the HW1 branch and commit them:

```
git add HW1/hw1.txt
git commit -m "Add new line"
```

8-9. Checkout "testing" branch, change "test_revert.txt", commit it and push this branch to the repo.

```
git checkout testing
git add HW1/test_revert.txt
git commit -m 'Make changes for revert testing'
git push  --set-upstream origin testing
```

10. Merge branch "testing" to "HW1".

```
git checkout HW1
git merge testing
git push
```

11. After merging testing into HW1:

- HW1 branch contains changes in the "test_revert.txt" from the "testing" branch and keeps changes in the "hw1.txt" file from the previous commit.
- HW1 points to the merge commit
- Branch "testing" points to the last commit before merge and has no additional changes since that time.


12. Revert the merge comit

My merge commit has two parents:

170f6a918d2e90678504a542775f26be0adf2476, c13e57db65e3e79d34eee053645da5cc205ba508

And I'm going to use the firts parent commit to keep in the reverted version.

```
git revert -m 1 bcbbaa621769a7b68ee5e361684bc27b4d19c270
```

13-14. Make changes to "test_revert_merge.txt" in the "testing" branch

```
git checkout testing
git add HW1/test_revert_merge.txt
git commit -m "Make changes to test revert merge"
git push
```

15. Second merge

```
git checkout HW1
git merge testing
```

The merge was successfull, but the contents of HW1 folder are not what I expected. There is a change in the "test_revert_merge.txt" but the previous change in the "test_revert.txt" from the "testing" branch has disappeared.

It seems that Git considers changes in reverted commits as never happend and looks only on those changes happend after the revert commit. Maybe it can be explained in such way that the merge commit is considered as a last common ancestor of those two branches.

16. Workaround

Initially I wanted to cherry-pick that commit, but in case there are many commits this might be not very convenient. So the solution with reverting the revert-commit seems to be preferable:

```
git revert -m 1 65f124882f89356d3abe266f264922057c98533b
git push
```

Now I've got also changes in the "test_revert.txt"