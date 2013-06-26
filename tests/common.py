import blueprint

class TestLayer(blueprint.TaskIterator):
    def __init__(self, name, **kwargs):
        blueprint.TaskIterator.__init__(self, name, **kwargs)
        self.afterInitSet = False
        self.setupSet = False
        self.beforeExecuteSet = False
        self.executeSet = False
        self.afterExecuteSet = False

    def _afterInit(self):
        self.afterInitSet = True

    def _setup(self):
        self.setupSet = True

    def _beforeExecute(self):
        self.beforeExecuteSet = True

    def _execute(self, frameset):
        self.executeSet = True

    def _afterExecute(self):
        self.afterExecuteSet = True

class TestTask(blueprint.Task):
    def __init__(self, name, **kwargs):
        blueprint.Task.__init__(self, name, **kwargs)
        self.afterInitSet = False
        self.setupSet = False
        self.beforeExecuteSet = False
        self.executeSet = False
        self.afterExecuteSet = False

    def _afterInit(self):
        self.afterInitSet = True

    def _setup(self):
        self.setupSet = True

    def _beforeExecute(self):
        self.beforeExecuteSet = True

    def _execute(self):
        self.executeSet = True

    def _afterExecute(self):
        self.afterExecuteSet = True