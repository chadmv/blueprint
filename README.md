### Blueprint
Blueprint is a job description library for the [Plow Render Farm](http://www.plowrender.com).  It simplifies the creation of a Plow job spec structure, allows execution of arbitrary python code on Plow, and provides hooks for integration into your existing pipeline

### Application Modules
A Blueprint application module is necessary for wrapping your application/code to run on Plow.  Blueprint will eventually include core modules for:

* Maya
* MotionBuiler
* Nuke
* Katana
* Blender
* Houdini
* Open Image IO

Also included are modules for executing arbitrary shell commands, python code, file search, and other pipeline related tasks.

### Plugins
Blueprint includes an event driven plugin system which can be used to intercept job events and execute arbitrary code.

### Dependencies

```
pip install pyyaml
pip install Fileseq
```