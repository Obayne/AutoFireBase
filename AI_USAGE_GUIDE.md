# How to Use Your AI Tools in VS Code

**Quick Start Guide for Local AI Integration**

---

## 🎯 **IMMEDIATE NEXT STEPS**

### **1. Open Continue Extension (Your Main AI Tool)**
- Look for the **Continue icon** in VS Code sidebar (robot/chat icon - usually looks like a chat bubble or AI brain)
- Click it to open the AI chat panel
- **At the top of the chat panel**, you'll see a **model dropdown menu**
- Click the dropdown and select **"DeepSeek Coder (Ollama)"** (it's the first option now)
- The dropdown shows all available AI models - local and cloud

### **2. Test Your Local AI**
- Type: `Explain what this project does`
- Press Enter
- You should get a response from your local DeepSeek Coder model

### **3. Try Code Assistance**
- Open any Python file (like `app/main.py`)
- Select some code with your mouse
- In Continue chat, type: `Explain this code`
- Or: `How can I improve this function?`

---

## 🤖 **YOUR AI TOOLS QUICK REFERENCE**

### **Primary Tools (Use These First)**

#### **1. Continue Extension (Most Powerful)**
**Location:** VS Code sidebar (robot icon)
**Best For:** Code explanations, suggestions, complex tasks

**How to Use:**
```
1. Click Continue icon
2. Select "DeepSeek Coder (Ollama)" model
3. Type your question or select code first
4. Ask things like:
   - "Explain this function"
   - "How do I add error handling?"
   - "Write a test for this code"
   - "Refactor this to be more readable"
```

#### **2. Tabnine (Automatic Code Completion)**
**Location:** Built into your typing
**Best For:** Speed coding, auto-complete

**How to Use:**
```
- Just start typing code
- Look for gray text suggestions
- Press Tab to accept
- Press Esc to ignore
```

#### **3. Claude Dev (Complex Tasks)**
**Location:** VS Code sidebar (usually right side)
**Best For:** Multi-step coding, debugging, project planning

---

## 💻 **DAILY AI WORKFLOW**

### **Morning Setup (5 minutes)**
```bash
# 1. Open VS Code
# 2. Open Continue chat
# 3. Select "DeepSeek Coder (Ollama)"
# 4. Ask: "What should I work on today?"
```

### **While Coding (Throughout Day)**
```
1. Write code normally
2. Use Tabnine for auto-complete
3. When stuck: Ask Continue "How do I...?"
4. For complex changes: Ask Claude Dev
5. Before committing: Run automation script
```

### **Example Session**
```
You: "I need to add a new device type to the catalog"
Continue: "Here's how to modify the device.py file..."
You: Implement the changes
Continue: "Now update the UI to show the new device"
You: Make UI changes
Claude Dev: "Run tests to make sure it works"
```

---

## 🔧 **SPECIFIC USE CASES**

### **Understanding Code**
```
Select code → Continue → "Explain what this does"
```

### **Writing New Code**
```
Continue → "Write a function to validate email addresses in Python"
```

### **Debugging Problems**
```
Continue → "This code has a bug, help me find it"
Paste error message
```

### **Learning New Concepts**
```
Continue → "Teach me about Python decorators"
```

### **Code Review**
```
Select code → Continue → "Review this code for best practices"
```

### **Testing**
```
Continue → "Write unit tests for this function"
```

---

## ⚙️ **ADVANCED FEATURES**

### **Context-Aware Chat**
- Continue can see your open files
- Reference specific files: `@app/main.py`
- Ask about project structure

### **Inline Edits**
- Continue can suggest changes directly in your code
- Click "Apply" to accept suggestions

### **Multiple Models**
- **DeepSeek Coder (Ollama)**: Fast, local, coding-focused, seamless VS Code integration
- **DeepSeek Coder (API)**: Cloud version, more powerful, no local resources needed
- **Claude**: Best for complex reasoning, can run commands and manage files
- **LM Studio**: GUI chat interface, model marketplace, conversation history (if configured)

### **Terminal Integration**
```bash
# Direct Ollama chat
ollama run deepseek-coder

# Then ask questions in terminal
```

---

## 🚨 **TROUBLESHOOTING**

### **Continue Not Working**
```
1. Check if Ollama is running: ollama list
2. Restart VS Code
3. Reload Continue extension
4. Check .continue/config.json is correct
```

### **Slow Responses**
```
- Close other applications
- Use smaller model if needed
- Switch to cloud models for complex tasks
```

### **Model Not Available**
```
- Run: ollama pull deepseek-coder:latest
- Or use cloud DeepSeek API
```

---

## 🎯 **WHEN TO USE EACH TOOL**

| Situation | Use This Tool | Why |
|-----------|---------------|-----|
| **Quick questions** | Continue (Ollama) | Fast, local, always available |
| **Complex coding** | Claude Dev | Better reasoning, can run commands |
| **Auto-complete** | Tabnine | Speed, no thinking required |
| **Learning** | Continue | Patient explanations |
| **Debugging** | Claude Dev | Can analyze entire codebase |
| **Code review** | Continue | Detailed feedback |
| **Writing tests** | Continue | Knows testing patterns |

---

## 📈 **GETTING BETTER RESULTS**

### **🎯 Give Your Agent Clear Directions**

**The AI is your coding assistant - tell it exactly what you want!**

#### **Be Specific About What You Want**
❌ "Help me with this code"
✅ "Fix the bug in this login function where it doesn't validate email format correctly"

#### **Provide Full Context**
❌ "Add error handling"
✅ "Add try/catch error handling to the file upload function in app/upload.py that currently crashes when files are too large"

#### **Break Complex Tasks Into Steps**
❌ "Build a user authentication system"
✅ "Step 1: Create a User model class with email/password fields
Step 2: Add password hashing using bcrypt
Step 3: Create login/register functions in auth.py"

#### **Specify File Locations**
❌ "Update the UI"
✅ "Modify app/main_window.py to add a 'Save Project' button to the toolbar"

#### **Include Technical Details**
❌ "Make it faster"
✅ "Optimize the database query in reports.py that loads 10,000 records - use pagination and add database indexing"

### **💬 Effective AI Communication Patterns**

#### **For Code Writing:**
```
"Write a Python function called validate_device_placement() that:
- Takes a device object and coordinates (x, y)
- Checks if the position conflicts with existing devices
- Returns True if valid, False if invalid
- Add type hints and a docstring"
```

#### **For Debugging:**
```
"This code crashes with 'AttributeError: 'NoneType' object has no attribute 'name''
The error occurs in the device placement function.
Help me find the bug and fix it."
```

#### **For Code Review:**
```
"Review this function for:
- Security vulnerabilities
- Performance issues
- Code style problems
- Missing error handling
Suggest specific improvements with code examples"
```

#### **For Learning:**
```
"Explain how Python decorators work with a simple example,
then show me how to create a @login_required decorator for my web app"
```

### **🔧 Use Code Selection Effectively**
- **Select specific code** before asking questions
- **Include surrounding context** (5-10 lines above/below)
- **Highlight the exact problem area**
- Continue will analyze the selected code specifically

### **📋 Task Planning with AI**

**Before starting complex work:**
```
"Plan how to implement user preferences saving:
1. What files need to be modified?
2. What data structure should we use?
3. How to handle default values?
4. Where to save the preferences file?"
```

**AI will give you a clear roadmap before you start coding!**

---

## 🔄 **INTEGRATION WITH AUTOMATION**

### **Before Committing Code**
```powershell
# Run automation to check your work
.\scripts\auto_complete.ps1
```

### **AI-Assisted Development Cycle**
```
1. Plan with Claude Dev
2. Code with Continue + Tabnine
3. Test with automation script
4. Debug with Claude Dev
5. Commit when clean
```

---

## 🎉 **YOU'RE READY TO CODE WITH AI!**

**Start Small:**
1. Open Continue
2. Select DeepSeek Coder (Ollama)
3. Ask: "Show me a simple Python example"
4. Build from there!

**Remember:** AI is your assistant, not your replacement. Use it to accelerate your learning and productivity!

**Need Help?** Ask any AI tool: "How do I get started with this project?"

---

**Pro Tip:** Keep this guide open in a VS Code tab while you work! 📖
