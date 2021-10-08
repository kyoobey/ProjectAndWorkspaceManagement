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



class PathInputHandler(sublime_plugin.TextInputHandler):

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

	def run(self, path):
		path = Path(path)
		project_name = path.name

		path.mkdir(parents=True)

		project_file_path = path / (project_name+'.sublime-project')
		# make project file
		with open(project_file_path, 'w') as f:
			f.write(DEFAULT_PROJECT_FILE_TEXT)

		path = path/'.sublime_workspaces'
		path.mkdir(parents=True)

		# make project file
		workspace_path = path / ('w1 '+project_name+'.sublime-workspace')
		with open(workspace_path, 'w') as f:
			f.write('{"project":"'+ str(project_file_path) +'"}')

		subl('-n', '--project', workspace_path)

	def input(self, args):
		return PathInputHandler()

	def input_description(self):
		return "Path"
