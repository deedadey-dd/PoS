# How to See the .venv Directory

The `.venv` directory has been created. It may not be visible in your IDE because:
1. It starts with a dot (hidden files/folders)
2. Your IDE may filter out hidden files by default

Here's how to make it visible:

## Windows File Explorer

1. Open File Explorer
2. Click the **View** tab
3. Check the box **"Hidden items"** in the Show/hide section
4. The `.venv` folder should now be visible

## VS Code

1. Open VS Code Settings (Ctrl+,)
2. Search for `files.exclude`
3. Look for patterns like `**/.venv` or `**/.*`
4. Either remove those patterns or set them to `false`
5. Or search for `files.exclude` and remove `.venv` from the list

Alternatively:
- Go to File → Preferences → Settings
- Search for "exclude"
- In "Files: Exclude", remove `.venv` pattern if it exists

## Cursor IDE / VS Code

**Option 1: Check settings file**
- A `.vscode/settings.json` file has been created in the project
- It's configured to show all files including `.venv`

**Option 2: Manual settings**
1. Open Settings (Ctrl+,)
2. Search for `files.exclude`
3. Look for any pattern like `**/.venv` and remove it (or set to `false`)
4. The folder should appear in the file explorer

**Note:** Even if `.venv` doesn't appear in the explorer, it exists and works. You can:
- Activate it from terminal: `.\.venv\Scripts\Activate.ps1`
- VS Code/Cursor should auto-detect it for Python interpreter selection

## Verify .venv Exists

Run this in PowerShell to verify:
```powershell
Test-Path .venv
Get-ChildItem .venv -Directory
```

## Note

Even if you can't see it in your IDE, the virtual environment is working. You can activate it with:
```powershell
.\.venv\Scripts\Activate.ps1
```

