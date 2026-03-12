# Obsidian Quick Start Guide

Quick reference for setting up Obsidian with the Engineer Knowledge System.

## Setup Steps

### 1. Open Vault
- Open Obsidian
- Select "Open folder as vault"
- Choose `knowledge-system/knowledge/` directory

### 2. Enable Community Plugins
- Settings → Community plugins
- Turn off restricted mode
- Browse and install "Obsidian Git"

### 3. Configure Git Remote
```bash
# In knowledge-system/ directory
git remote add origin http://localhost:3001/admin/knowledge-system.git

# Or with SSH (recommended)
git remote add origin git@localhost:2222/admin/knowledge-system.git
```

### 4. Configure Obsidian Git Plugin
- Settings → Community plugins → Obsidian Git
- Commit message: `vault backup: {{date}}`
- Auto backup interval: `10` minutes
- Auto pull interval: `10` minutes
- Enable "Auto pull on boot"
- Enable "Pull before push"

### 5. Test Sync
- Create a test note
- Use `Ctrl/Cmd + Shift + K` to commit
- Use `Ctrl/Cmd + Shift + P` to push
- Check Gitea web interface for the commit

## Keyboard Shortcuts

- `Ctrl/Cmd + Shift + K` - Commit changes
- `Ctrl/Cmd + Shift + P` - Push to remote
- `Ctrl/Cmd + Shift + L` - Pull from remote
- `Ctrl/Cmd + Shift + G` - Open graph view

## Knowledge Structure

```
knowledge/
├── 01-foundations/     # Core CS concepts
├── 02-technologies/    # Specific technologies
├── 03-architecture/    # Architecture patterns
├── 04-projects/        # Project experiences
└── 05-insights/        # Personal insights
```

## Recommended Plugins

1. **Obsidian Git** - Auto sync with Git
2. **Dataview** - Dynamic queries
3. **Templater** - Template automation
4. **Calendar** - Daily notes

## Troubleshooting

**Can't push?**
- Check Git credentials
- Verify SSH key is added to Gitea
- Try manual `git push` in terminal

**Merge conflicts?**
- Open terminal in `knowledge-system/`
- Run `git status` to see conflicts
- Edit files to resolve conflicts
- Run `git add .` and `git commit`

**Auto sync not working?**
- Check plugin is enabled
- Verify interval settings
- Check developer console for errors

For detailed instructions, see `OBSIDIAN-SETUP-GUIDE.md`.
