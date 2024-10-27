
from git import Repo
import subprocess
from . BuildException import BuildException


class Code:
    

    def __init__(
        self, path, buildcmd, workdir=None, branch=None,
        commit=None, remote='origin', url=None
    ):
        """
        Constructor.
        """
        self.workdir = workdir
        self.path = path
        self.buildcmd = buildcmd.format(path=path)
        self.branch = branch
        self.remote = remote
        self.url = url
        self.repo = Repo(path)

        if branch is None:
            pot = ['master', 'main']
            for b in pot:
                if b in self.repo.branches:
                    self.branch = b
                    break

            if self.branch is None:
                self.branch = self.repo.branches[0].name

        if commit is not None:
            self.synchronize(commit)
        else:
            self.synchronize()


    def build(self):
        """
        Build the code.
        """
        cmd = self.buildcmd.split(' ')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.workdir)
        out, err = p.communicate()

        if p.returncode != 0:
            raise BuildException(
                f"The build process exited with a non-zero exit code.\n\n{err.decode('utf-8')}",
                out=out.decode('utf-8'), err=err.decode('utf-8')
            )


    def getCommit(self):
        """
        Get the commit number of the code.
        """
        return self.repo.head.commit.hexsha


    def synchronize(self, commit=None):
        """
        Synchronize the repository to the latest version.
        """
        if self.remote not in self.repo.remotes:
            raise Exception(f"No remote '{self.remote}' in repository.")

        remote = self.repo.remotes[self.remote]

        # Update index
        remote.fetch()

        # Check if selected branch is tracked
        if self.branch not in self.repo.branches:
            # Setup new branch and track remote branch
            if self.branch not in remote.refs:
                raise Exception(f"No branch named '{self.branch}' on the remote '{remote.name}'.")

            ref = remote.refs[self.branch]
            self.repo.create_head(self.branch, ref)
            self.repo.branches[self.branch].set_tracking_branch(ref)

        if commit is not None:
            # Find the commit
            c = self.repo.commit(commit)
            self.repo.git.checkout(c.hexsha)
        else:
            # Find the branch
            branch = None
            for b in self.repo.branches:
                if b.name == self.branch:
                    branch = b
                    break

            if branch is None:
                raise Exception(f"No branch '{self.branch}' in repository.")

            branch.checkout()
            remote.pull()


