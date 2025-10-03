# Free CI/CD Agents & Setup Commands

**Date:** October 3, 2025
**Project:** AutoFire - Fire Alarm CAD Application
**Focus:** Free CI/CD services with setup commands

---

## 📋 Available Free CI/CD Services

### 1. **GitHub Actions** ⭐ (Currently Configured)
**Free Tier:** 2,000 minutes/month for public repos, 500 minutes/month for private repos
**Best For:** GitHub-hosted projects, seamless integration

#### Setup Commands
```bash
# GitHub Actions is already configured in your repo
# Check existing workflows
ls .github/workflows/

# View current CI configuration
cat .github/workflows/ci.yml
```

#### Configuration Already in Place
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt -r requirements-dev.txt
      - name: Lint
        run: ruff check .
      - name: Format check
        run: black --check .
      - name: Run tests
        run: pytest -q
```

#### Additional Free Actions You Can Add
```yaml
# Add to .github/workflows/ci.yml
- name: Security audit
  run: pip audit

- name: Type checking
  run: mypy frontend/ backend/ cad_core/

- name: Coverage report
  run: pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

---

### 2. **GitLab CI/CD** 🏆
**Free Tier:** 400 minutes/month, unlimited public repos
**Best For:** Self-hosted option available, great for private repos

#### Setup Commands (If Migrating)
```bash
# Create .gitlab-ci.yml in project root
cat > .gitlab-ci.yml << 'EOF'
stages:
  - test
  - build

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt -r requirements-dev.txt
  script:
    - ruff check .
    - black --check .
    - pytest -q
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  image: python:3.11
  before_script:
    - pip install pyinstaller
  script:
    - pyinstaller --noconfirm AutoFire.spec
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - main
    - tags
EOF

# Push to GitLab repository
git add .gitlab-ci.yml
git commit -m "ci: Add GitLab CI/CD configuration"
git push origin main
```

#### GitLab Runner (Self-hosted Option)
```bash
# Install GitLab Runner on your machine
# Download from: https://docs.gitlab.com/runner/install/

# Register runner (Linux/Windows)
sudo gitlab-runner register

# Enter your GitLab instance URL
# Enter registration token from project settings
# Choose executor (docker, shell, etc.)

# Start runner
sudo gitlab-runner start
```

---

### 3. **CircleCI** 🔄
**Free Tier:** 6,000 minutes/month for open source, 2,500 minutes/month for private repos
**Best For:** Fast builds, great Docker support

#### Setup Commands
```bash
# Create .circleci/config.yml
mkdir -p .circleci
cat > .circleci/config.yml << 'EOF'
version: 2.1

orbs:
  python: circleci/python@2.1.1

workflows:
  test-and-build:
    jobs:
      - test
      - build:
          requires:
            - test
          filters:
            branches:
              only: main

jobs:
  test:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          app-dir: .
          pip-requirements-file: requirements-dev.txt
      - run:
          name: Install core dependencies
          command: pip install -r requirements.txt
      - run:
          name: Run linter
          command: ruff check .
      - run:
          name: Check formatting
          command: black --check .
      - run:
          name: Run tests
          command: pytest -q --cov=. --cov-report=xml
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: coverage.xml

  build:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install PyInstaller
          command: pip install pyinstaller
      - run:
          name: Build executable
          command: pyinstaller --noconfirm AutoFire.spec
      - store_artifacts:
          path: dist/
EOF

# Commit and push
git add .circleci/
git commit -m "ci: Add CircleCI configuration"
git push origin main
```

---

### 4. **AppVeyor** 🪟
**Free Tier:** Unlimited for open source projects
**Best For:** Windows-focused projects, great for PyInstaller builds

#### Setup Commands
```bash
# Create appveyor.yml in project root
cat > appveyor.yml << 'EOF'
image: Visual Studio 2022

environment:
  PYTHON: "C:\\Python311-x64"

install:
  - "SET PATH=%PYTHON%;%PYTHON%\\Scripts;%PATH%"
  - pip install -r requirements.txt
  - pip install -r requirements-dev.txt

build_script:
  - ruff check .
  - black --check .
  - pytest -q

after_build:
  - pip install pyinstaller
  - pyinstaller --noconfirm AutoFire.spec

artifacts:
  - path: dist\AutoFire
    name: AutoFire-Windows
    type: zip

deploy:
  - provider: GitHub
    auth_token:
      secure: YOUR_ENCRYPTED_TOKEN
    artifact: AutoFire-Windows
    on:
      branch: main
EOF

# Commit configuration
git add appveyor.yml
git commit -m "ci: Add AppVeyor CI configuration"
git push origin main
```

---

### 5. **Travis CI** 🏗️
**Free Tier:** 10,000 credits/month for private repos, unlimited for public
**Best For:** Simple setups, good documentation

#### Setup Commands
```bash
# Create .travis.yml
cat > .travis.yml << 'EOF'
language: python
python:
  - "3.11"

cache:
  directories:
    - $HOME/.cache/pip

install:
  - pip install -r requirements.txt
  - pip install -r requirements-dev.txt

script:
  - ruff check .
  - black --check .
  - pytest -q

deploy:
  provider: releases
  api_key: $GITHUB_TOKEN
  file: dist/AutoFire/AutoFire.exe
  skip_cleanup: true
  on:
    tags: true
    python: "3.11"

before_deploy:
  - pip install pyinstaller
  - pyinstaller --noconfirm AutoFire.spec
EOF

# Enable Travis CI for your repository at travis-ci.com
# Add GITHUB_TOKEN to Travis CI environment variables
```

---

### 6. **Azure DevOps Pipelines** ☁️
**Free Tier:** 1,800 minutes/month for open source projects
**Best For:** Enterprise features, great integration with Microsoft tools

#### Setup Commands
```bash
# Create azure-pipelines.yml
cat > azure-pipelines.yml << 'EOF'
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
  displayName: 'Install dependencies'

- script: |
    ruff check .
    black --check .
  displayName: 'Code quality checks'

- script: |
    pytest -q --cov=. --cov-report=xml
  displayName: 'Run tests'

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'test-results.xml'
    testRunTitle: 'Python Tests'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: 'coverage.xml'

- script: |
    pip install pyinstaller
    pyinstaller --noconfirm AutoFire.spec
  displayName: 'Build executable'
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))

- task: PublishBuildArtifacts@1
  inputs:
    pathtoPublish: 'dist'
    artifactName: 'AutoFire-Linux'
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
EOF

# Import into Azure DevOps project
# Go to Pipelines → Create Pipeline → GitHub
# Select your repository and use existing YAML
```

---

### 7. **Buildkite** 🚀
**Free Tier:** 100 builds/month for free tier
**Best For:** Self-hosted agents, great for custom infrastructure

#### Setup Commands
```bash
# Install Buildkite Agent (Linux)
curl -sSL https://bootstrap.buildkite.com/install | bash

# Configure agent
buildkite-agent configure

# Enter your agent token from Buildkite dashboard
# Set build path and other options

# Create pipeline.yml
cat > pipeline.yml << 'EOF'
steps:
  - label: "Test Suite"
    command: |
      pip install -r requirements.txt -r requirements-dev.txt
      ruff check .
      black --check .
      pytest -q --cov=. --cov-report=xml
    artifact_paths: "coverage.xml"

  - label: "Build Release"
    command: |
      pip install pyinstaller
      pyinstaller --noconfirm AutoFire.spec
    artifact_paths: "dist/**/*"
    branches: "main"
EOF

# Upload pipeline to Buildkite dashboard
```

---

### 8. **Drone CI** 🛸
**Free Tier:** Unlimited for public repos, 1GB logs for free tier
**Best For:** Docker-native, simple YAML configuration

#### Setup Commands
```bash
# Create .drone.yml
cat > .drone.yml << 'EOF'
kind: pipeline
type: docker
name: test-and-build

steps:
- name: test
  image: python:3.11
  commands:
    - pip install -r requirements.txt -r requirements-dev.txt
    - ruff check .
    - black --check .
    - pytest -q --cov=. --cov-report=xml

- name: build
  image: python:3.11
  commands:
    - pip install pyinstaller
    - pyinstaller --noconfirm AutoFire.spec
  when:
    branch:
      - main
    event:
      - push

- name: deploy
  image: plugins/github-release
  settings:
    api_key:
      from_secret: github_token
    files:
      - dist/AutoFire/AutoFire.exe
  when:
    event:
      - tag
EOF

# Enable Drone CI for your repository
# Add secrets in Drone CI dashboard
```

---

## 🆚 Comparison Table

| Service | Free Minutes/Month | Best For | Setup Complexity |
|---------|-------------------|----------|------------------|
| GitHub Actions | 2,000 (public) | GitHub integration | Low |
| GitLab CI/CD | 400 | Self-hosted option | Medium |
| CircleCI | 6,000 (OSS) | Docker, speed | Low |
| AppVeyor | Unlimited (OSS) | Windows builds | Low |
| Travis CI | 10,000 credits | Simple setups | Low |
| Azure DevOps | 1,800 (OSS) | Enterprise features | Medium |
| Buildkite | 100 builds | Custom infrastructure | High |
| Drone CI | Unlimited (public) | Docker-native | Medium |

---

## 🚀 Quick Setup Recommendations

### For AutoFire (Python/PySide6/Windows focus):
1. **GitHub Actions** (already configured) - Primary CI
2. **AppVeyor** - Windows-specific builds
3. **CircleCI** - Fast alternative

### Minimal Setup (3 services):
```bash
# 1. GitHub Actions (already done)
# 2. Add AppVeyor for Windows builds
# Create appveyor.yml as shown above

# 3. Add CircleCI for fast builds
# Create .circleci/config.yml as shown above
```

### Advanced Setup (Full coverage):
- **GitHub Actions**: Primary CI/CD
- **AppVeyor**: Windows builds
- **CircleCI**: Linux builds
- **GitLab CI/CD**: Self-hosted option

---

## 🔧 Common CI/CD Commands

### Status Checks
```bash
# GitHub Actions status
curl -s https://api.github.com/repos/Obayne/AutoFireBase/actions/runs | jq '.workflow_runs[0].status'

# View build logs
# Visit https://github.com/Obayne/AutoFireBase/actions
```

### Local CI Simulation
```bash
# Simulate CI pipeline locally
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
black --check .
pytest -q
pyinstaller --noconfirm AutoFire.spec
```

### CI Configuration Validation
```bash
# Validate GitHub Actions locally
act -j build --container-architecture linux/amd64

# Validate CircleCI locally
circleci config validate .circleci/config.yml

# Validate GitLab CI locally
gitlab-ci-pipelines-multi-project --validate .gitlab-ci.yml
```

---

**Note:** Most services offer free tiers for open source projects. Choose based on your target platforms (Windows for AutoFire) and existing repository location.
