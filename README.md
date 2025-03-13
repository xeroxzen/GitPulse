# **GitPulse** 🚀

**Know Your Contributions. Measure Your Impact.**

**Code is intellectual property and should be treated as such. Know your contributions and value added.**

GitPulse is a powerful tool for analyzing Git repositories, providing insights into contributor statistics, language usage, and more. It works with both local Git repositories and remote GitHub repositories.

## **🔹 Features**

✅ **Commit Counts** – See how many commits each contributor has made.  
✅ **Pull Request Insights** – Track PRs opened and merged per user.  
✅ **Language Contributions** – Understand which languages each contributor has worked on.  
✅ **Lines of Code Analysis** – Identify meaningful code contributions per user.  
✅ **Issue Tracking** – View issues opened and closed per contributor.  
✅ **Percentage Contribution** – Measure the overall contribution of each developer to the codebase.  
✅ **Top Languages** – Discover the dominant languages in a repository.  
✅ **Contributor Analysis**: See who contributed the most to a repository  
✅ **Contribution Percentages**: View each contributor's percentage of total changes  
✅ **Language Statistics**: Analyze which programming languages are used in the repository  
✅ **GitHub Integration**: Analyze remote GitHub repositories using the GitHub API

## **⚡ Usage**

GitPulse can be used as:

- A **CLI tool** for quick repo analysis.
- A **Web App** for visualizing and comparing contributions across repositories.

## **🚀 Get Started**

🔹 **CLI:** Install and run GitPulse to analyze a local or GitHub repository.  
🔹 **Web App:** Upload or link a repo to get instant contribution insights.

> _Your code tells a story. Let GitPulse help you understand it._

---

## **👨‍💻 Author**

**[Andile Jaden Mbele](https://github.com/xeroxzen)**  
🚀 Software Engineer | Data Engineer | AI Enthusiast  
📌 CEO @ **Vectra Dynamics**  
💡 Passionate about building technology that empowers people

🌍 _Follow my work_

- GitHub: [@xeroxzen](https://github.com/xeroxzen)
- Twitter: [@andilejaden](https://twitter.com/andilejaden)
- LinkedIn: [Andile Jaden Mbele](https://www.linkedin.com/in/andilejaden-mbele/)

---

## **🔧 Installation**

```bash
# Clone the repository
git clone https://github.com/yourusername/GitPulse.git
cd GitPulse

# Install dependencies
pip install -r requirements.txt

# Set up GitHub token (for remote repository analysis)
echo "GITHUB_TOKEN=your_github_token" > .env
```

## **🔧 Usage**

### **Command Line Interface**

GitPulse provides a simple command-line interface for analyzing repositories:

```bash
# Analyze a local repository
./test_contributions.py --local /path/to/local/repo

# Analyze a remote GitHub repository
./test_contributions.py --remote https://github.com/username/repo

# Analyze the current directory (must be a Git repository)
./test_contributions.py
```

### **Python API**

You can also use GitPulse as a library in your Python code:

```python
from gitpulse.core.repository import Repository

# Analyze a local repository
local_repo = Repository("/path/to/local/repo", is_remote=False)
local_repo.display_contribution_stats()
local_repo.display_language_stats()

# Analyze a remote GitHub repository
github_repo = Repository("https://github.com/username/repo", is_remote=True)
github_repo.display_contribution_stats()
github_repo.display_language_stats()

# Get raw data for custom analysis
contributors = github_repo.get_contributor_stats()
languages = github_repo.get_top_languages()
percentages = github_repo.get_contribution_percentages()
```

## **🔧 GitHub Authentication**

For analyzing remote GitHub repositories, you need to authenticate with the GitHub API:

1. Create a GitHub Personal Access Token:

   - Go to GitHub.com → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name and select the necessary scopes (at minimum, you'll need `repo` access)
   - Copy the generated token

2. Set the token in your environment:
   - Create a `.env` file in the project root with: `GITHUB_TOKEN=your_token_here`
   - Or set it as an environment variable: `export GITHUB_TOKEN=your_token_here`

## **🔧 Example Output**

### **Contribution Statistics**

```
                       Repository Contribution Statistics
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Contributor ┃ Commits ┃ Lines Added ┃ Lines Deleted ┃ Files Changed ┃ Total Changes ┃ Percentage ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ user1       │     42 │       2500 │         500 │          120 │         3000 │     75.0% │
│ user2       │     15 │        800 │         200 │           50 │         1000 │     25.0% │
└─────────────┴────────┴────────────┴─────────────┴──────────────┴──────────────┴───────────┘
```

### **Language Statistics**

```
                    Repository Language Statistics
┏━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Language ┃ Lines of Code ┃ Percentage ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Python   │        10000 │      80.0% │
│ HTML     │         1500 │      12.0% │
│ CSS      │          500 │       4.0% │
│ JavaScript │          500 │       4.0% │
└──────────┴──────────────┴────────────┘
```

## **🤝 Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## **📄 License**

This project is licensed under the MIT License - see the LICENSE file for details.
