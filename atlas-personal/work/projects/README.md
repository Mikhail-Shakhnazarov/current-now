# Projects

Work lives here. Each project is a self-contained folder.

See `INDEX.md` for the human-friendly project list.

## Structure

```
projects/
|-- <project-name>/
|   |-- now.md          # Current position in this project
|   |-- specs/          # Executable specifications
|   |-- src/            # Implementation (for code projects)
|   |-- logs/
|   |   `-- changelog.md
|   `-- .atlas/
|       `-- version     # Desk version that created this
```

## Portability

Projects are portable between desk versions:
1. Check `.atlas/version` against current desk
2. Apply migration if breaking changes
3. Continue working

## Creating a Project

Use templates in `desk/templates/`:
- `desk/templates/project-devOS.md`
- `desk/templates/project-writeOS.md`

Then create folder, add `now.md` pointing to first action, add `.atlas/version` with current desk version. Start interpreting.
