
from git import Repo
import subprocess
from . BuildException import BuildException


class Code:
    

    def __init__(self, path, buildcmd, workdir=None, branch=None, commit=None, remote='origin'):
        """
        Constructor.
        """
        self.workdir = workdir
        self.path = path
        self.buildcmd = buildcmd.format(path=path)
        self.branch = branch
        self.remote = remote
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
        remote = None
        for r in self.repo.remotes:
            if r.name == self.remote:
                remote = r
                break

        if remote is None:
            raise Exception(f"No remote '{self.remote}' in repository.")

        # Update index
        remote.fetch()

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


