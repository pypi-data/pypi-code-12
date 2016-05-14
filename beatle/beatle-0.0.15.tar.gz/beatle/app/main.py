#import gettext

import os
import wx
import pickle
from  ctx import theContext as context
from ctx import logger
import app
import tran

# _globals = sys.modules[__name__]

use_splash = False


class proCxx(wx.App):
    """Clase aplicacion"""
    # theApp = None

    def OnInit(self):
        """Inicializacion de GUI"""
        global use_splash
        #self.presLan_en = gettext.translation("proCxx", "./locale",
        #     languages=['en'])
        #self.locale = wx.Locale(wxLANGUAGE_ENGLISH)
        #locale.setlocale(locale.LC_ALL, 'EN')
        #self.presLan_en.install()
        self.projects = []
        self.workspaces = []
        if use_splash:
            splash = app.AppSplashScreen()
            splash.Show()
        else:
            app.mainWindow(self)
            context.frame.Show()
            wx.GetApp().SetTopWindow(context.frame)
        stack = tran.TransactionStack(50)
        self.log = logger()
        self.log.SetFile('.proCxx.log')
        wx.Log.EnableLogging()
        stack.SetLogger(self.log)
        context.app = self
        return True

    def ExitEvenModified(self):
        """Checks about unsaved documents"""
        chain = ""
        for project in self.projects:
            if project.IsModified():
                chain += "\n" + project._name
        if len(chain) > 0:
            user = wx.MessageBox("The projects: " + chain +
            " \nhave unsaved changes.\nExit anyway?", "Alert",
                wx.YES_NO | wx.CENTER | wx.ICON_HAND, context.frame)
            if user != wx.YES:
                return False
        self.log.Dump()
        return True

    def ExistProject(self, name):
        """Comprueba si el proyecto ya esta cargado"""
        for project in self.projects:
            if project._name == name:
                return True
        return False

    def AddProject(self, project):
        """Crea un objeto de proyecto y lo incorpora a la lista interna"""
        if project not in self.projects:
            self.projects.append(project)
        return project

    def AddWorkspace(self, workspace):
        """Crea un objeto de workspace y lo incorpora a la lista interna"""
        if workspace not in self.workspaces:
            self.workspaces.append(workspace)
        return workspace

    def RemoveProject(self, project):
        """Elimina un proyecto de la lista interna"""
        while project in self.projects:
            index = self.projects.index(project)
            del self.projects[index]

    def SaveProject(self, project):
        """Almacena un proyecto"""
        if not project in self.projects:
            wx.MessageBox("Project " + project._name + " not exists", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
            return
        project_dir = project._dir.replace("//", "/")
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            if not os.path.exists(project_dir):
                wx.MessageBox("Failed creating projec directory:\n" +
                    project_dir, "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return
        fname = (project_dir + "/" + project._name + ".pcc").replace("//", "/")
        with open(fname, "w") as f:
            pickle.dump(project, f, 2)
        project.SetModified(False)
        if project.workspace is None:
            mru = context.mru
            mru.AddFileToHistory(fname)

    def SaveSession(self):
        """Save the current session"""
        wl = self.GetSessionWorkspaces()  # workspace's path
        if not wl:
            return False
        context.config.Write('/last_session/workspaces', str(wl))
        tl = context.frame.GetViewsStatus()  # get the open views status
        context.config.Write('/last_session/views', str(tl))
        return True

    @tran.TransactionalMethod('reload last session')
    def LoadSession(self):
        """Read last session"""
        wl = context.config.Read('/last_session/workspaces', '')
        if not wl:
            return False
        wl = eval(wl)  # restore list
        if not self.SetSessionWorkspaces(wl):
            return False
        tl = context.config.Read('/last_session/views', '')
        if not tl:
            return True
        tl = eval(tl)
        if tl:
            context.frame.SetViewsStatus(tl)
        return True

    def SaveWorkspace(self, wrkspace):
        """Save the workspace and projects"""
        import model
        workspace_dir = wrkspace._dir.replace("//", "/")
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)
            if not os.path.exists(workspace_dir):
                wx.MessageBox("Failed creating workspace directory:\n" +
                    workspace_dir, "Error",
                    wx.OK | wx.CENTER | wx.ICON_ERROR, context.frame)
                return
        for project in wrkspace[model.Project]:
            self.SaveProject(project)
        fname = (workspace_dir + "/" + wrkspace._name + ".wrk").replace("//", "/")
        with open(fname, "w") as f:
            pickle.dump(wrkspace, f, 2)
        wrkspace.SetModified(False)
        mru = context.mru
        mru.AddFileToHistory(fname)

    def GetSessionWorkspaces(self):
        """Save full list of opened workspaces. This is a tentative.
        If some workspace is unsave, returns False. Otherwise,
        returns the workspace list."""
        files = []
        for wrk in self.workspaces:
            if wrk._modified:
                return False
            _dir = wrk._dir.replace("//", "/")
            fname = (_dir + "/" + wrk._name + ".wrk").replace("//", "/")
            files.append(fname)
        return files

    def SetSessionWorkspaces(self, files):
        """Attempts to load worskpaces"""
        status = True
        for fname in files:
            workspace = self.LoadWorkspace(fname)
            if workspace:
                tran.TransactionStack.DoLoad(workspace)
            else:
                status = False
        return status

    def LoadProject(self, fname, workspace=None, skip_compare=False):
        """Carga un proyecto existente"""
        # reload workspace must avoid waste time checking duplicates
        if not skip_compare:
            for project in self.projects:
                already_fname = (project._dir + "/" + project._name +
                    ".pcc").replace("//", "/")
                print(("compare " + already_fname + " with " + fname + "\n"))
                if already_fname == fname:
                    return None
        import traceback
        import sys
        import model
        try:
            with open(fname, "r") as f:
                project = pickle.load(f)
            if not isinstance(project, model.Project):
                return None
            if workspace:
                workspace.addChild(project)
                project._parent = workspace
            self.projects.append(project)
            project.SetModified(False)
            # check classes
            for cls in project.classes:
                if cls.errorCheckDerivatives():
                    project.SetModified(True)
            return project
        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            return None

    def LoadWorkspace(self, fname):
        """Carga un workspace existente"""
        import traceback
        import sys
        import model
        for workspace in self.workspaces:
            already_fname = (workspace._dir + "/" + workspace._name +
                ".pcc").replace("//", "/")
            print(("compare " + already_fname + " with " + fname + "\n"))
            if already_fname == fname:
                return None
        try:
            with open(fname, "r") as f:
                workspace = pickle.load(f)
            if not isinstance(workspace, model.Workspace):
                return False
            self.workspaces.append(workspace)
            workspace.SetModified(False)
            mru = context.mru
            mru.AddFileToHistory(fname)
            return workspace
        except Exception as inst:
            traceback.print_exc(file=sys.stdout)
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            return None


