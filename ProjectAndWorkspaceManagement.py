import sublime
import sublime_plugin
from pathlib import Path
import os
import json
import subprocess


SETTINGS_FILE_NAME = "ProjectAndWorkspaceManagement.sublime-settings"



#####################
# helper functions

def set_platform_specific_path(platform, path):
	if type(path)!=str: path = str(path)
	if platform == 'windows':
		path = path.replace("\\",'/')
		path = '/'+path.replace(':','')
	return path

def get_platform_specific_path(platform, path):
	if type(path)!=str: path = str(path)
	if platform == 'windows':
		path = path[1]+':\\'+path[2:].replace('/', '\\')
	return path

def workspaces_path():
	return sublime.load_settings(SETTINGS_FILE_NAME)['workspaces_subpath'].strip('/').strip('\\')



variables = None

#####################
# function taken from
# https://github.com/randy3k/ProjectManager/blob/fdfd0372cf8ef705ac8a6c352e9c6ce21df1b0de/project_manager.py#L52
def subl(*args):
	executable_path = sublime.executable_path()
	if sublime.platform() == 'osx':
		app_path = executable_path[:executable_path.rfind('.app/') + 5]
		executable_path = app_path + 'Contents/SharedSupport/bin/subl'

	subprocess.Popen([executable_path] + list(args))

	def on_activated():
		window = sublime.active_window()
		view = window.active_view()

		if sublime.platform() == 'windows':
			# fix focus on windows
			window.run_command('focus_neighboring_group')
			window.focus_view(view)

		sublime_plugin.on_activated(view.id())
		sublime.set_timeout_async(lambda: sublime_plugin.on_activated_async(view.id()))

	sublime.set_timeout(on_activated, 300)



class NewProjectPathInputHandler(sublime_plugin.TextInputHandler):

	def initial_text(self):
		return sublime.load_settings(SETTINGS_FILE_NAME)['default_project_path']

	def placeholder(Self):
		return "Enter full project path"

	def description(self, text):
		return 'path'

	def preview(self, text):
		if Path(os.path.expanduser(text)).exists():
			return sublime.Html(f"<b>Path already exists</b>")
		return sublime.Html(f"<strong>Creating Project at </strong> <em>{text}</em>")

	def validate(self, text):
		if Path(os.path.expanduser(text)).exists():
			return False
		return True



class ProjectAndWorkspaceManagementNewProjectCommand(sublime_plugin.ApplicationCommand):

	def run(self, new_project_path):
		path = Path(os.path.expanduser(new_project_path))
		project_name = path.name

		path.mkdir(parents=True)

		project_file_path = path / (project_name+'.sublime-project')
		# make project file
		with open(project_file_path, 'w') as f:
			f.write(sublime.load_settings(SETTINGS_FILE_NAME)['default_project_file_text'])

		gitignore_file_path = path / '.gitignore'
		# make .gitignore file
		with open(gitignore_file_path, 'w') as f:
			f.write(sublime.load_settings(SETTINGS_FILE_NAME)['default_gitignore_file_text'])

		path = path / workspaces_path()
		path.mkdir(parents=True)

		# make workspace file inside workspace folder
		workspace_path = path / ('w1 '+project_name+'.sublime-workspace')
		with open(workspace_path, 'w') as f:
			if sublime.platform() == "windows":
				project_file_path = str(project_file_path).replace("\\",'/')
				project_file_path = '/'+project_file_path.replace(':','')
			f.write('{"project":"'+ str(project_file_path) +'"}')

		subl('-n', '--project', workspace_path)

	def input(self, args):
		return NewProjectPathInputHandler()

	def input_description(self):
		return "Path"



class NewWorkspaceNameInputHandler(sublime_plugin.TextInputHandler):

	def initial_text(self):
		global variables
		if 'project_name' in variables.keys():
			try:
				if (Path(variables['project_path']) / (f'{workspaces_path()}/w1 '+variables['project_base_name']+'.sublime-workspace')).exists():
					n = sorted([int(x.name.split(' ')[0][1:]) for x in (Path(variables['project_path']) / workspaces_path()).glob('**/*')])[-1]
					return f'w{str(n+1)} {variables["project_base_name"]}'
			except Exception:
				pass
		return 'workspace name'

	def placeholder(Self):
		return "Enter new workspace name"

	def description(self, text):
		return 'name'

	def preview(self, text):
		if (Path(variables['project_path']) / (f'{workspaces_path()}/{text}.sublime-workspace')).exists():
			return sublime.Html(f"<b>Workspace already exists</b>")
		return sublime.Html(f"<strong>Creating New workspace</strong> <em>{text}</em>")

	def validate(self, text):
		if (Path(variables['project_path']) / (f'{workspaces_path()}/{text}.sublime-workspace')).exists():
			return False
		return True



class ProjectAndWorkspaceManagementNewWorkspaceCommand(sublime_plugin.WindowCommand):

	def run(self, new_workspace_name):
		path = Path(variables['project_path']) / workspaces_path()
		if not path.exists():
			path.mkdir(parents=True)

		# make workspace file inside workspace folder
		workspace_path = path / (new_workspace_name+'.sublime-workspace')
		with open(workspace_path, 'w') as f:
			project_file_path = set_platform_specific_path(sublime.platform(), variables['project'])
			f.write('{"project":"'+ project_file_path +'"}')

		subl('--project', workspace_path)

	def input(self, args):
		global variables
		variables = self.window.extract_variables()

		return NewWorkspaceNameInputHandler()

	def input_description(self):
		return "Name"



class OpenWorkspaceIndexInputHandler(sublime_plugin.ListInputHandler):

	def list_items(self):
		try:
			path = Path(variables['project_path']) / f'{workspaces_path()}/'
			self.file_name_paths = [x for x in (path).glob('**/*') if x.is_file()]
			self.file_names = [x.name.replace('.sublime-workspace','') for x in self.file_name_paths]
			return [(x, i) for i,x in enumerate(self.file_names)]
		except Exception:
			return [(' ', -1)]

	def preview(self, value):
		try:
			if not (Path(variables['project_path']) / f'{workspaces_path()}/').exists():
				return sublime.Html(f"<b>No workspaces found</b>")
		except Exception:
			return sublime.Html("No open projects")
		return sublime.Html(f"<strong>Opening workspace</strong> {self.file_names[value]}")

	def validate(self, value):
		try:
			if (Path(variables['project_path']) / f'{workspaces_path()}/').exists():
				return True
		except Exception:
			pass
		return False



class ProjectAndWorkspaceManagementOpenWorkspaceCommand(sublime_plugin.WindowCommand):

	def run(self, open_workspace_index):
		path = Path(variables['project_path']) / f'{workspaces_path()}/'
		file_names = [x for x in (path).glob('**/*') if x.is_file()]

		subl('--project', file_names[open_workspace_index])

	def input(self, args):
		global variables
		variables = self.window.extract_variables()

		return OpenWorkspaceIndexInputHandler()

	def input_description(self):
		return "Workspace"



class GetWorkspaceIndexToRenameInputHandler(sublime_plugin.ListInputHandler):

	def list_items(self):
		try:
			path = Path(variables['project_path']) / f'{workspaces_path()}/'
			self.file_name_paths = [x for x in (path).glob('**/*') if x.is_file()]
			self.file_names = [x.name.replace('.sublime-workspace','') for x in self.file_name_paths]
			return [(x, i) for i,x in enumerate(self.file_names)]
		except Exception:
			return [(' ', -1)]

	def preview(self, value):
		try:
			if not (Path(variables['project_path']) / workspaces_path()).exists():
				return sublime.Html(f"<b>No workspaces found</b>")
		except Exception:
			return sublime.Html("No open projects")
		return sublime.Html(f"<strong>Renaming workspace</strong> {self.file_names[value]}")

	def validate(self, value):
		try:
			if (Path(variables['project_path']) / workspaces_path()).exists():
				return True
		except Exception:
			pass
		return False

	def next_input(self, args):
		return RenameWorkspaceNameInputHandler()


class RenameWorkspaceNameInputHandler(sublime_plugin.TextInputHandler):

	def initial_text(self):
		return 'New workspace name'

	def preview(self, value):
		return f"renaming to {value}.sublime-workspace"



class ProjectAndWorkspaceManagementRenameWorkspaceCommand(sublime_plugin.WindowCommand):

	def run(self, get_workspace_index_to_rename, rename_workspace_name):
		path = Path(variables['project_path']) / workspaces_path()
		current_workspace_path = [x for x in (path).glob('**/*') if x.is_file()][get_workspace_index_to_rename]
		new_path = Path(current_workspace_path.parent, rename_workspace_name + current_workspace_path.suffix)

		current_workspace_path.rename(new_path)
		subl('--project', new_path)

	def input(self, args):
		global variables
		variables = self.window.extract_variables()

		if not args.get('open_workspace'):
			return GetWorkspaceIndexToRenameInputHandler()

		if not args.get('rename_workspace_name'):
			return RenameWorkspaceNameInputHandler()

	def input_description(self):
		return "Rename Workspace"



class GetWorkspaceIndexToDeleteInputHandler(sublime_plugin.ListInputHandler):

	def list_items(self):
		r = []
		try:
			path = Path(variables['project_path']) / workspaces_path()
			self.file_name_paths = [x for x in (path).glob('**/*') if x.is_file()]
			self.file_names = [x.name.replace('.sublime-workspace','') for x in self.file_name_paths]
			r += [(x, i) for i,x in enumerate(self.file_names)]
		except Exception:
			pass
		if len(r)<1: r += [(' ', -1)]
		return r

	def preview(self, value):
		try:
			if (Path(variables['project_path']) / workspaces_path()).exists():
				if any((Path(variables['project_path']) / workspaces_path()).iterdir()):
					return sublime.Html(f"<strong>Deleting workspace</strong> {self.file_names[value]}")
		except Exception:
			return sublime.Html("No open projects")
		return sublime.Html(f"<b>No workspaces found</b>")

	def validate(self, value):
		try:
			if (Path(variables['project_path']) / workspaces_path()).exists():
				if any((Path(variables['project_path']) / workspaces_path()).iterdir()):
					return True
		except Exception:
			pass
		return False



class ProjectAndWorkspaceManagementDeleteWorkspaceCommand(sublime_plugin.WindowCommand):

	def run(self, get_workspace_index_to_delete):
		path = Path(variables['project_path']) / workspaces_path()
		current_workspace_path = [x for x in (path).glob('**/*') if x.is_file()][get_workspace_index_to_delete]

		current_workspace_path.unlink()

	def input(self, args):
		global variables
		variables = self.window.extract_variables()
		return GetWorkspaceIndexToDeleteInputHandler()

	def input_description(self):
		return "Delete Workspace"



class ProjectAndWorkspaceManagementCreateProjectFilesAtExistingFolderCommand(sublime_plugin.WindowCommand):

	def run(self):
		global variables
		variables = self.window.extract_variables()
		path = Path(variables['folder'])
		project_name = path.name

		# path.mkdir(parents=True)

		project_file_path = path / (project_name+'.sublime-project')
		# make project file
		with open(project_file_path, 'w') as f:
			f.write(sublime.load_settings(SETTINGS_FILE_NAME)['default_project_file_text'])

		gitignore_file_path = path / '.gitignore'
		# make .gitignore file
		with open(gitignore_file_path, 'w') as f:
			f.write(sublime.load_settings(SETTINGS_FILE_NAME)['default_gitignore_file_text'])

		try:
			path = path / workspaces_path()
			path.mkdir(parents=True)

			# make workspace file inside workspace folder
			workspace_path = path / ('w1 '+project_name+'.sublime-workspace')
			with open(workspace_path, 'w') as f:
				if sublime.platform() == "windows":
					project_file_path = str(project_file_path).replace("\\",'/')
					project_file_path = '/'+project_file_path.replace(':','')
				f.write('{"project":"'+ str(project_file_path) +'"}')
		except Exception as e:
			pass

		subl('-n', '--project', workspace_path)


class projectAndWorkspaceManagementImportProjectFilesAtCurrentFolder(sublime_plugin.WindowCommand):

	def run(self):
		global variables
		variables = self.window.extract_variables()
		path = Path(variables['folder'])
		project_name = path.name

		workspaces_data = []
		for workspace_file_path in path.glob(f'{workspaces_path()}/*.sublime-workspace'):
			with open(workspace_file_path, 'r') as workspace_file:
				workspaces_data.append((json.loads(workspace_file.read()), workspace_file_path))
		
		for (workspace_data, workspace_file_path) in workspaces_data:
			old_project_name = workspace_data['project'].split('/')[-2]
			old_project_path = '/'.join(workspace_data['project'].split('/')[:-1])

			for buffer_data in workspace_data['buffers']:
				buffer_data['file'] = set_platform_specific_path(sublime.platform(), path) + buffer_data['file'].replace(old_project_path, '')

			workspace_data['expanded_folders'] = [ set_platform_specific_path(sublime.platform(), path) + expanded_folder_data.replace(old_project_path, '') for expanded_folder_data in workspace_data['expanded_folders'] ]

			for group_data in workspace_data['groups']:
				for sheet_data in group_data['sheets']:
					sheet_data['file'] = set_platform_specific_path(sublime.platform(), path) + sheet_data['file'].replace(old_project_path, '')

			workspace_data['project'] = set_platform_specific_path(sublime.platform(), path / (path.name+'.sublime-project'))

			new_workspace_file_path = str(workspace_file_path).replace(old_project_name, path.name)
			with open(new_workspace_file_path, 'w') as f:
				f.write(json.dumps(workspace_data))

			subl('-n', '--project', new_workspace_file_path)

		for _, p in workspaces_data:
			os.remove(p)

		for project_file_path in path.glob('*.sublime-project'):
			os.rename(project_file_path, str(project_file_path).replace(project_file_path.name.replace('.sublime-project', ''), path.name))


