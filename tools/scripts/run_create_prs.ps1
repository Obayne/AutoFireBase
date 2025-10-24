Set-Location 'C:\Dev\Autofire'
# Do NOT hard-code token file paths in repo scripts. Set one of these in your environment:
#  - $env:GITHUB_PAT (recommended)
#  - $env:GITHUB_PAT_FILE (path to a file containing the token)
python .\tools\github_create_prs.py --owner Obayne --repo AutoFireBase
