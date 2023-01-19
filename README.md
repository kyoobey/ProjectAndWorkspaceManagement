# Project And Workspace Management
A Project and Workspace Management plugin for [Sublime Text 4](https://www.sublimetext.com).
> This project was inspired by https://github.com/randy3k/ProjectManager

# Functionality
This plugin helps you manage your sublime workspace files. You can create and quickly switch between multiple workspaces for a single sublime text project. Extra functionality to be added (see [Todo Section](https://github.com/tshrpl/ProjectManagement#Todo)).
> Please open the one of the `.sublime-workspace` files to open a project because opening the `.sublime-project` file will create a new workspace at the root instead of the hidden folder!

# Commands
| Commands       | Function |
|----------------|----------|
| Edit Settings  | Opens a window with the default, non-editable settings on the left and user overrides file on the right, closes when the user file is closed |
| New Project    | Creates new project files (`<project>.sublime-project`, `.sublime-workspaces` folder and `.gitignore`) at the specified path |
| New Workspace  | Creates new workspace file inside `.sublime-workspaces` folder |
| Open Workspace | Opens existing workspace in a new window |
| Rename Workspace | Renames existing workspace and opens it in a new window |
| Delete Workspace | Deletes existing workspace |
| Create Project at existing folder | Create Project files at currently open folder (if any) |
| Import Project Files At Current Folder | Edits `workspace` files inside `.sublime_workspaces/` to work with the new project path and rename Project/Workspace files (__use with caution__ and __only use once on a copied/moved project__)

# Settings
| Commands                       | Function |
|--------------------------------|----------|
| `default_project_path`         | default value for `New Project` input |
| `workspaces_subpath`           | properly formatted path to store workspaces to (e.g. `.sublime-workspaces`, `.sublime/workspaces`) |
| `default_project_file_text`    | properly formatted json text for `<project>.sublime-project` file |
| `default_gitignore_file_text`  | properly formatted json text for `.gitignore` file |

# Todo
- [ ] store and search for existing project files on disk
- [ ] support for centralization (absolute paths in `workspaces_subpath` and/or `default_project_path`)

# License
Project And Workspace Management is [MIT licensed](https://github.com/tshrpl/ProjectManagement/blob/master/LICENSE.txt).
