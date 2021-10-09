import sublime
import sublime_plugin
from pathlib import Path
import subprocess



DEFAULT_PROJECT_FILE_TEXT = """{
	"folders":
	[
		{
			"path": ".",
			"folder_exclude_patterns": [".sublime_workspaces"]
		}
	]
}"""


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
		return "/projects/<full_project_path>"

	def placeholder(Self):
		return "Enter full project path"

	def description(self, text):
		return 'path'

	def preview(self, text):
		if Path(text).exists():
			return sublime.Html(f"<b>Path already exists</b>")
		return sublime.Html(f"<strong>Creating Project at </strong> <em>{text}</em>")

	def validate(self, text):
		if Path(text).exists():
			return False
		return True



class NewProjectCommand(sublime_plugin.ApplicationCommand):

	def run(self, new_project_path):
		path = Path(new_project_path)
		project_name = path.name

		path.mkdir(parents=True)

		project_file_path = path / (project_name+'.sublime-project')
		# make project file
		with open(project_file_path, 'w') as f:
			f.write(DEFAULT_PROJECT_FILE_TEXT)

		gitignore_file_path = path / '.gitignore'
		# make .gitignore file
		print(gitignore_file_path)
		with open(gitignore_file_path, 'w') as f:
			f.write('#folders\n.sublime_workspaces/')

		path = path/'.sublime_workspaces'
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
				if (Path(variables['project_path']) / ('.sublime_workspaces/w1 '+variables['project_base_name']+'.sublime-workspace')).exists():
					n = sorted([int(x.name.split(' ')[0][1:]) for x in (Path(variables['project_path']) / '.sublime_workspaces').glob('**/*')])[-1]
					return f'w{str(n+1)} {variables["project_base_name"]}'
			except Exception:
				pass
		return 'workspace name'

	def placeholder(Self):
		return "Enter new workspace name"

	def description(self, text):
		return 'name'

	def preview(self, text):
		if (Path(variables['project_path']) / (f'.sublime_workspaces/{text}.sublime-workspace')).exists():
			return sublime.Html(f"<b>Workspace already exists</b>")
		return sublime.Html(f"<strong>Creating New workspace</strong> <em>{text}</em>")

	def validate(self, text):
		if (Path(variables['project_path']) / (f'.sublime_workspaces/{text}.sublime-workspace')).exists():
			return False
		return True



variables = None

class NewWorkspaceCommand(sublime_plugin.WindowCommand):

	def run(self, new_workspace_name):
		path = Path(variables['project_path']) / '.sublime_workspaces'
		if not path.exists():
			path.mkdir(parents=True)

		# make workspace file inside workspace folder
		workspace_path = path / (new_workspace_name+'.sublime-workspace')
		with open(workspace_path, 'w') as f:
			project_file_path = variables['project']
			if sublime.platform() == "windows":
				project_file_path = project_file_path.replace("\\",'/')
				project_file_path = '/'+project_file_path.replace(':','')
				print(project_file_path)
			f.write('{"project":"'+ project_file_path +'"}')

		subl('--project', workspace_path)

	def input(self, args):
		global variables
		variables = self.window.extract_variables()

		return NewWorkspaceNameInputHandler()

	def input_description(self):
		return "Name"

