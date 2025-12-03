# AI Automation Specification for AutoFire Project
## Beginner's Guide to VS Code Automation & AI Tools

**Last Updated:** November 12, 2025
**For:** Developers with limited programming experience

---

## 🚀 QUICK START: Getting Your Project Running in VS Code

### Step 1: Open Your Project
1. **Launch VS Code** (the blue icon with "</>" symbol)
2. **Open your project folder:**
   - Click `File` → `Open Folder`
   - Navigate to `C:\Dev\Autofire`
   - Click `Select Folder`

### Step 2: Trust the Workspace
- VS Code will ask: "Do you trust the authors of the files in this folder?"
- Click **"Yes, I trust the authors"**

### Step 3: Check Your Setup
- Look at the bottom-right corner of VS Code
- You should see: `Python 3.x.x` (if not, click it and select your Python version)
- The left sidebar should show your project files

### Step 4: Run Your First Automation
Open a terminal in VS Code:
- Press `` Ctrl + ` `` (backtick) or View → Terminal
- Type: `.\scripts\automated_dev_workflow.ps1 -All`
- Press Enter

---

## 🤖 AI AUTOMATION TOOLS EXPLAINED

### What is AI Automation?
AI automation means computers help you write code, catch mistakes, and manage your work automatically. Instead of doing everything manually, AI tools assist you like a smart assistant.

### Your AI Tools Ecosystem

#### **Cloud-Based AI (Currently Active)**

##### 1. **Claude Dev** (Your Main AI Assistant)
- **What it does:** Helps you write code, answer questions, and automate tasks
- **How to use it:**
  - Look for the "Claude Dev" chat panel (usually on the right side)
  - Type questions like "explain this code" or "help me fix this error"
  - It can write code for you and run commands
- **Best for:** Complex coding tasks, debugging, project planning

##### 2. **Tabnine** (AI Code Completion)
- **What it does:** Predicts what you're going to type next
- **How it works:**
  - As you type code, it suggests completions
  - Press `Tab` to accept suggestions
  - Learns from your coding style over time
- **Best for:** Speed coding, reducing keystrokes

##### 3. **CodeStream** (Code Review Assistant)
- **What it does:** Helps with code reviews and discussions
- **When to use:** When working with others on code changes

#### **Local AI Options (Multiple Choices Available)**

Since you have **both LM Studio and Ollama** installed with **DeepSeek Coder**, you have excellent local AI capabilities! Here's how they integrate with your VS Code automation:

##### **🎯 Your Local AI Setup**
- **LM Studio:** GUI-based model manager with chat interface
- **Ollama:** Command-line focused, lightweight model runner
- **DeepSeek Coder:** Specialized coding model you already have installed

##### **🔒 Privacy & Security Advantages**
- **Complete local processing** - Code stays on your machine
- **No cloud data sharing** - Perfect for sensitive projects
- **Offline capability** - Works without internet
- **Full control** - You manage all models and data

##### **💰 Cost Benefits**
- **Zero API costs** - No subscriptions or usage fees
- **Free models** - Download once, use forever
- **Hardware only** - Just electricity costs

##### **⚡ Performance Advantages**
- **Low latency** - No network delays
- **Specialized models** - DeepSeek Coder optimized for programming
- **Concurrent usage** - Run multiple models simultaneously

##### **Ollama + DeepSeek Coder Integration**

###### **Quick Setup in VS Code:**

1. **Verify Ollama is running:**
   ```bash
   ollama list
   ```
   You should see `deepseek-coder` in the list.

2. **Start DeepSeek Coder:**
   ```bash
   ollama run deepseek-coder
   ```

3. **VS Code Extensions for Ollama:**
   - ✅ **Continue extension installed** (supports local models)
   - Configure Continue to use `http://localhost:11434` (Ollama's default port)
   - Alternative: Use VS Code's built-in terminal for Ollama commands

###### **Using DeepSeek Coder in VS Code:**

**Option A: Ollama Extension**
- Provides chat interface directly in VS Code
- Ask coding questions: "How do I implement a Python class?"
- Get code suggestions and explanations

**Option B: Continue Extension**
- More advanced AI coding assistant
- Can reference your open files
- Inline code suggestions
- Chat with context awareness

**Option C: Terminal Integration**
- Use in VS Code terminal: `ollama run deepseek-coder`
- Interactive chat for complex coding problems
- Save conversations for reference

##### **LM Studio vs Ollama: Detailed Comparison**

| Feature | LM Studio | Ollama | Winner |
|---------|-----------|---------|--------|
| **Interface** | Beautiful GUI chat app with chat history, model switching, and visual model management | Command-line focused, lightweight | **LM Studio** (better UX) |
| **VS Code Integration** | Requires manual API server setup | Direct Continue extension support | **Ollama** (seamless) |
| **Model Management** | Visual download/install, easy model switching, model marketplace | Command-line downloads, simple but less visual | **LM Studio** (easier) |
| **Resource Usage** | Higher memory usage (GUI overhead) | Lower resource usage (CLI only) | **Ollama** (efficient) |
| **DeepSeek Coder** | ✅ Available via download | ✅ Pre-installed and tested | **Tie** |
| **Setup Time** | 2-3 minutes (download model) | 1 minute (already running) | **Ollama** (faster) |
| **Chat Experience** | Full chat interface with history, personas, and advanced features | Basic terminal chat | **LM Studio** (richer) |
| **API Access** | Built-in local API server | Built-in API server | **Tie** |
| **Multi-Model** | Easy switching between models | Single model at a time in terminal | **LM Studio** (better) |

##### **When LM Studio Wins:**

**🎯 Use LM Studio if you prefer:**
- **Visual interface** - GUI chat app feels more modern
- **Easy model management** - Download models with one click
- **Chat history** - Keep conversations and reference them
- **Multiple models** - Switch between different AIs easily
- **Beginner-friendly** - Less technical setup
- **Advanced features** - Personas, chat templates, advanced settings

**💪 LM Studio Advantages:**
- **Better UX**: Full chat application with modern interface
- **Model Marketplace**: Browse and download models visually
- **Chat Management**: Save and organize conversations
- **Advanced Settings**: Temperature, context length, etc. via GUI
- **Cross-Platform**: Same experience on Windows/Mac/Linux
- **Backup/Restore**: Easy model backup and sharing

##### **When Ollama Wins:**

**🎯 Use Ollama if you want:**
- **VS Code integration** - Direct Continue extension support
- **Performance** - Lower resource usage
- **Simplicity** - Minimal setup, just works
- **Automation** - Better for scripted workflows
- **Speed** - Faster startup and response times

**💪 Ollama Advantages:**
- **VS Code Native**: Continue extension works out-of-the-box
- **Lightweight**: Less memory and CPU usage
- **Fast Startup**: Instant model loading
- **Automation Ready**: Perfect for scripts and workflows
- **Pre-configured**: DeepSeek Coder already installed and tested

##### **Complete AI Workflow Strategy**

**Your AI Tools Hierarchy:**

1. **Claude Dev (Primary)** - Complex coding, debugging, project planning
2. **DeepSeek Coder (Ollama)** - Code suggestions, explanations, research
3. **Tabnine** - Real-time code completion
4. **LM Studio** - Backup when Ollama is busy, model experimentation

**Daily Usage Pattern:**
- **Morning:** Claude Dev for planning and complex tasks
- **Coding:** Tabnine for completion + DeepSeek Coder for questions
- **Debugging:** Claude Dev or DeepSeek Coder for problem-solving
- **Learning:** LM Studio for experimenting with different models

##### **VS Code Integration Setup**

1. **✅ Continue Extension Installed:**
   - The Continue extension has been successfully installed in your VS Code

2. **✅ Ollama API Verified:**
   - Ollama server is running on `http://localhost:11434`
   - DeepSeek Coder models are available: `deepseek-coder:latest`, `deepseek-coder:base`

3. **✅ Continue Configured for Ollama:**
   - The `.continue/config.json` has been updated with Ollama integration
   - DeepSeek Coder (Ollama) is now available as the first model option
   - Configuration:
     ```json
     {
       "title": "DeepSeek Coder (Ollama)",
       "provider": "ollama",
       "model": "deepseek-coder:latest",
       "apiBase": "http://localhost:11434"
     }
     ```

3. **Alternative: Use VS Code Terminal:**
   - Open terminal in VS Code: `` Ctrl + ` ``
   - Run: `ollama run deepseek-coder`
   - Chat directly with DeepSeek Coder in the terminal

4. **Test Integration:**
   - Look for Continue icon in VS Code sidebar (usually a robot/chat icon)
   - Click it to open Continue chat
   - Select "DeepSeek Coder (Ollama)" as your model
   - Ask: "Explain this Python function" (with code selected)
   - Should get intelligent responses from your local DeepSeek Coder

##### **When to Use Each Local AI Tool**

**Use DeepSeek Coder (Ollama) when:**
- Need code explanations or suggestions
- Working in VS Code and want seamless integration
- Prefer command-line style interaction
- Want fast, lightweight AI assistance

**Use LM Studio when:**
- Want GUI chat interface
- Experimenting with different models
- Need visual model management
- Ollama is not available or busy

**Use Claude Dev when:**
- Complex multi-step coding tasks
- Need polished, production-ready code
- Working on architectural decisions
- Internet is available and speed is priority

##### **Optimizing DeepSeek Coder Performance**

1. **Model Size Consideration:**
   - You have DeepSeek Coder installed
   - Larger models = better quality but slower
   - Test different sizes: `deepseek-coder:6.7b`, `deepseek-coder:33b`

2. **Hardware Optimization:**
   ```bash
   # Check available models
   ollama list

   # Pull specific version if needed
   ollama pull deepseek-coder:6.7b
   ```

3. **VS Code Memory Management:**
   - Close unused tabs to free memory
   - Restart VS Code periodically
   - Monitor system resources when running AI models

---

## ⚙️ AUTOMATION EXTENSIONS BREAKDOWN

### Code Quality & Formatting Tools

#### **Prettier** (Code Formatter)
- **Purpose:** Makes your code look neat and consistent
- **What it does:** Automatically formats JavaScript, HTML, CSS, etc.
- **How it helps:** No more arguing about code style - it's automatic!
- **Usage:** Saves automatically when you save files

#### **Black** (Python Formatter)
- **Purpose:** Formats Python code to look professional
- **What it does:** Standardizes spacing, line breaks, etc.
- **How to use:** Run `python -m black .` in terminal

#### **ESLint** (JavaScript Checker)
- **Purpose:** Finds mistakes in JavaScript/TypeScript code
- **What it does:** Catches errors before you run the code
- **How it helps:** Prevents bugs and enforces good practices

#### **Pylint** (Python Checker)
- **Purpose:** Analyzes Python code for issues
- **What it does:** Rates your code quality and finds problems
- **Score:** Aims for 10/10 (perfect code)

### Productivity Tools

#### **Auto Rename Tag** (HTML Helper)
- **Purpose:** Keeps HTML tags matched
- **What it does:** When you change `<div>` to `<section>`, it automatically changes `</div>` to `</section>`

#### **Path Intellisense** (File Helper)
- **Purpose:** Helps you type file paths
- **What it does:** Suggests file names as you type `import` statements

#### **Code Runner** (Quick Tester)
- **Purpose:** Run code snippets instantly
- **How to use:**
  - Right-click on code
  - Select "Run Code"
  - See results in output panel

#### **REST Client** (API Tester)
- **Purpose:** Test web APIs without leaving VS Code
- **How to use:** Create `.http` files and click "Send Request"

#### **Todo Tree** (Task Manager)
- **Purpose:** Tracks all your TODO notes
- **What it does:** Shows a tree view of all `TODO`, `FIXME`, `XXX` comments
- **How to view:** Look for "TODOs" in the sidebar

#### **Better Comments** (Comment Organizer)
- **Purpose:** Makes comments stand out
- **What it does:** Colors different types of comments:
  - `!` Important notes (red)
  - `?` Questions (blue)
  - `//` Regular comments (gray)
  - `*` Highlights (yellow)

### Git & Version Control Tools

#### **GitLens** (Git Superpowers)
- **Purpose:** Advanced Git features
- **Features:**
  - See who wrote each line of code (blame)
  - Compare file versions
  - View commit history
- **How to use:** Click the GitLens icon in the sidebar

#### **Git Graph** (Visual Git History)
- **Purpose:** See your Git history as a graph
- **What it shows:** Branch merges, commits, authors
- **How to use:** Open Command Palette (`Ctrl+Shift+P`) → "Git Graph: View Git Graph"

#### **GitHub Pull Requests** (PR Manager)
- **Purpose:** Manage GitHub pull requests
- **What it does:** Review, approve, merge PRs from VS Code

#### **Conventional Commits** (Standard Messages)
- **Purpose:** Makes commit messages consistent
- **Format:** `type(scope): description`
- **Examples:**
  - `feat(login): add password reset`
  - `fix(api): handle null responses`
  - `docs(readme): update installation steps`

### Workflow Automation Tools

#### **Task Explorer** (Build Tasks)
- **Purpose:** Run npm/yarn scripts easily
- **How to use:** Look for "Task Explorer" in sidebar

#### **Run on Save** (Auto-Runner)
- **Purpose:** Run commands automatically when you save
- **Example:** Auto-format code on save

#### **Live Server** (Web Preview)
- **Purpose:** Preview web pages with auto-reload
- **How to use:**
  - Right-click HTML file
  - Select "Open with Live Server"

---

## 🎯 STEP-BY-STEP AUTOMATION WORKFLOW

### Daily Development Routine

1. **Morning Setup:**
   - Open VS Code
   - Open your project
   - Run: `.\scripts\automated_dev_workflow.ps1 -All`

2. **While Coding:**
   - Let Prettier/Black format your code automatically
   - Use Tabnine for code suggestions
   - ESLint/Pylint will show problems in real-time

3. **Before Committing:**
   - Check Todo Tree for unfinished tasks
   - Run tests: `.\scripts\automated_dev_workflow.ps1 -Test`
   - Check Git status: `.\scripts\automated_dev_workflow.ps1 -GitStatus`

4. **Commit Process:**
   - Use Conventional Commits for message format
   - Push changes via GitLens or terminal

### Troubleshooting Common Issues

#### "Command not found" errors:
- Make sure Python is installed and selected in VS Code
- Check that scripts are in the `scripts/` folder

#### Extensions not working:
- Go to Extensions sidebar (Ctrl+Shift+X)
- Make sure all extensions are enabled
- Reload VS Code: `Ctrl+Shift+P` → "Developer: Reload Window"

#### Git issues:
- Check GitLens for repository status
- Use `git status` in terminal to see current state

---

## 🧠 AI ASSISTANCE GUIDELINES

### When to Ask Claude Dev for Help

**Good questions:**
- "How do I fix this error?"
- "Explain what this code does"
- "Help me write a function to..."
- "What's the best way to structure this?"

**What Claude Dev can do:**
- Write code for you
- Debug problems
- Explain complex concepts
- Run terminal commands
- Create files and folders

### AI Code Completion (Tabnine)

**Tips for better suggestions:**
- Write clear variable names
- Follow consistent patterns
- Let it learn your style (use it regularly)

**When suggestions appear:**
- Gray text = AI suggestion
- Press `Tab` to accept
- Press `Esc` to ignore

---

## 📊 AUTOMATION METRICS & MONITORING

### What the Automation Script Checks

1. **Code Formatting:** Is code properly formatted?
2. **Code Quality:** Any linting errors?
3. **Tests:** Do all tests pass?
4. **Tasks:** Any unfinished TODOs?
5. **Git Status:** Current repository state

### Interpreting Results

**✅ Green messages:** Everything is good
**⚠️ Yellow messages:** Warnings (not critical)
**🔴 Red messages:** Errors that need fixing

### Regular Maintenance

**Weekly tasks:**
- Run full automation: `.\scripts\automated_dev_workflow.ps1 -All`
- Check for extension updates
- Review TODO list

**Monthly tasks:**
- Clean up old branches
- Archive completed projects
- Update dependencies

---

## 🎓 LEARNING RESOURCES

### Beginner-Friendly VS Code Tutorials
- VS Code "Getting Started" (built-in: Help → Getting Started)
- Official VS Code Docs: `https://code.visualstudio.com/docs`

### Python Learning
- Automate the Boring Stuff with Python (free online book)
- Python for Everybody (free course)

### Git Learning
- GitHub Learning Lab (interactive tutorials)
- "Oh Shit, Git!?" (quick reference)

### AI Assistance
- Ask Claude Dev: "Teach me about [topic]"
- Use Tabnine to learn coding patterns

---

## 🔧 ADVANCED FEATURES (When You're Ready)

### Custom Automation Scripts
You can modify `scripts/automated_dev_workflow.ps1` to:
- Add new checks
- Change file paths
- Add custom commands

### VS Code Settings
Access via `File` → `Preferences` → `Settings`:
- Customize extension behavior
- Set up auto-save
- Configure themes

### Keyboard Shortcuts
Learn these for speed:
- `Ctrl+P`: Quick file open
- `Ctrl+Shift+P`: Command palette
- `Ctrl+Shift+F`: Find in files
- `F12`: Go to definition

---

## 📞 GETTING HELP

### When Something Goes Wrong

1. **Check the automation script:**
   ```powershell
   .\scripts\automated_dev_workflow.ps1
   ```
   (without -All to see help)

2. **Ask Claude Dev:**
   - "I'm getting an error with [describe problem]"
   - "How do I [what you're trying to do]"

3. **Check VS Code Status:**
   - Bottom bar shows Python version, Git branch, errors
   - Extensions sidebar shows which tools are active

### Emergency Recovery
If VS Code acts strange:
- **Quick Reload:** `Ctrl+Shift+P` → Type "reload" → Select "Developer: Reload Window"
- **Alternative Reload:** Close all VS Code windows and reopen
- **Full Restart:** Close VS Code completely, then reopen
- **Check Task Manager:** End any stuck VS Code processes

---

**Remember:** Automation is about making your work easier, not more complicated. Start with the basics and gradually explore more features as you get comfortable. The AI tools are here to help you learn and work more efficiently! 🚀
