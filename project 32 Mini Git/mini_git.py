import os
import json
import hashlib
import shutil
from datetime import datetime

class MiniGit:
    def __init__(self):
        self.repo_dir = ".mini_git"
        self.commits_dir = os.path.join(self.repo_dir, "commits")
        self.staging_dir = os.path.join(self.repo_dir, "staging")
        self.head_file = os.path.join(self.repo_dir, "HEAD")
        self.branches_file = os.path.join(self.repo_dir, "branches.json")
        
    def init(self):
        """Initialize repository"""
        if os.path.exists(self.repo_dir):
            print("Repository already initialized")
            return
        os.makedirs(self.commits_dir)
        os.makedirs(self.staging_dir)
        with open(self.head_file, 'w') as f:
            f.write("master:")
        with open(self.branches_file, 'w') as f:
            json.dump({"master": None}, f)
        print("Initialized empty Mini Git repository")
    
    def add(self, filename):
        """Add file to staging area"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository. Run 'init' first")
            return
        if not os.path.exists(filename):
            print(f"File '{filename}' not found")
            return
        shutil.copy(filename, self.staging_dir)
        print(f"Added '{filename}' to staging area")
    
    def commit(self, message):
        """Commit staged files"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository")
            return
        
        staged_files = os.listdir(self.staging_dir)
        if not staged_files:
            print("Nothing to commit")
            return
        
        # Get current branch and parent commit
        with open(self.head_file, 'r') as f:
            head_content = f.read().strip()
        branch, parent = head_content.split(':') if ':' in head_content else (head_content, None)
        
        # Create commit data
        commit_data = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "parent": parent if parent else None,
            "files": {}
        }
        
        # Store file contents
        for file in staged_files:
            file_path = os.path.join(self.staging_dir, file)
            with open(file_path, 'r') as f:
                commit_data["files"][file] = f.read()
        
        # Generate commit hash
        commit_hash = hashlib.sha1(json.dumps(commit_data, sort_keys=True).encode()).hexdigest()[:8]
        
        # Save commit
        commit_file = os.path.join(self.commits_dir, f"{commit_hash}.json")
        with open(commit_file, 'w') as f:
            json.dump(commit_data, f, indent=2)
        
        # Update HEAD and branch
        with open(self.head_file, 'w') as f:
            f.write(f"{branch}:{commit_hash}")
        
        with open(self.branches_file, 'r') as f:
            branches = json.load(f)
        branches[branch] = commit_hash
        with open(self.branches_file, 'w') as f:
            json.dump(branches, f)
        
        # Clear staging
        for file in staged_files:
            os.remove(os.path.join(self.staging_dir, file))
        
        print(f"[{branch} {commit_hash}] {message}")
    
    def checkout(self, target):
        """Checkout commit or branch"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository")
            return
        
        with open(self.branches_file, 'r') as f:
            branches = json.load(f)
        
        # Check if target is a branch
        if target in branches:
            commit_hash = branches[target]
            if not commit_hash:
                print(f"Branch '{target}' has no commits")
                return
            with open(self.head_file, 'w') as f:
                f.write(f"{target}:{commit_hash}")
            print(f"Switched to branch '{target}'")
        else:
            commit_hash = target
            with open(self.head_file, 'r') as f:
                branch = f.read().split(':')[0]
            with open(self.head_file, 'w') as f:
                f.write(f"{branch}:{commit_hash}")
        
        # Load commit files
        commit_file = os.path.join(self.commits_dir, f"{commit_hash}.json")
        if not os.path.exists(commit_file):
            print(f"Commit '{commit_hash}' not found")
            return
        
        with open(commit_file, 'r') as f:
            commit_data = json.load(f)
        
        # Restore files
        for filename, content in commit_data["files"].items():
            with open(filename, 'w') as f:
                f.write(content)
        print(f"Checked out commit {commit_hash}")
    
    def branch(self, branch_name):
        """Create new branch"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository")
            return
        
        with open(self.branches_file, 'r') as f:
            branches = json.load(f)
        
        if branch_name in branches:
            print(f"Branch '{branch_name}' already exists")
            return
        
        # Get current commit
        with open(self.head_file, 'r') as f:
            head_content = f.read().strip()
        current_commit = head_content.split(':')[1] if ':' in head_content else None
        
        branches[branch_name] = current_commit
        with open(self.branches_file, 'w') as f:
            json.dump(branches, f)
        print(f"Created branch '{branch_name}'")
    
    def log(self):
        """Show commit history"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository")
            return
        
        with open(self.head_file, 'r') as f:
            head_content = f.read().strip()
        
        if ':' not in head_content:
            print("No commits yet")
            return
        
        current_commit = head_content.split(':')[1]
        
        while current_commit:
            commit_file = os.path.join(self.commits_dir, f"{current_commit}.json")
            if not os.path.exists(commit_file):
                break
            
            with open(commit_file, 'r') as f:
                commit_data = json.load(f)
            
            print(f"\nCommit: {current_commit}")
            print(f"Date: {commit_data['timestamp']}")
            print(f"Message: {commit_data['message']}")
            
            current_commit = commit_data.get('parent')
    
    def status(self):
        """Show repository status"""
        if not os.path.exists(self.repo_dir):
            print("Not a Mini Git repository")
            return
        
        with open(self.head_file, 'r') as f:
            head_content = f.read().strip()
        branch = head_content.split(':')[0]
        
        print(f"On branch: {branch}")
        
        staged_files = os.listdir(self.staging_dir)
        if staged_files:
            print("\nStaged files:")
            for file in staged_files:
                print(f"  {file}")
        else:
            print("\nNo files staged")

def main():
    git = MiniGit()
    
    print("=== Mini Git Version Control System ===\n")
    print("Commands: init, add <file>, commit <message>, checkout <commit/branch>, branch <name>, log, status, exit\n")
    
    while True:
        try:
            cmd = input("mini-git> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            command = parts[0]
            
            if command == "init":
                git.init()
            elif command == "add":
                if len(parts) < 2:
                    print("Usage: add <filename>")
                else:
                    git.add(parts[1])
            elif command == "commit":
                if len(parts) < 2:
                    print("Usage: commit <message>")
                else:
                    git.commit(parts[1])
            elif command == "checkout":
                if len(parts) < 2:
                    print("Usage: checkout <commit_hash/branch>")
                else:
                    git.checkout(parts[1])
            elif command == "branch":
                if len(parts) < 2:
                    print("Usage: branch <branch_name>")
                else:
                    git.branch(parts[1])
            elif command == "log":
                git.log()
            elif command == "status":
                git.status()
            elif command == "exit":
                print("Goodbye!")
                break
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
