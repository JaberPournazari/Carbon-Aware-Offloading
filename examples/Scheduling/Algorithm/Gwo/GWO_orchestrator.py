from examples.Scheduling.comparing_orchestrator import comparing_orchestrator
from examples.Scheduling.Algorithm.Gwo.GWO import TaskDeviceScheduler



class GWOOrchestrator(comparing_orchestrator):
    def __init__(self, infrastructure, applications, devices, tasks, carbon=False, lb=-100, ub=100, dim=30, SearchAgents_no=30
                 , Max_iter=1000):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure = infrastructure
        self.applications = applications
        self.Max_iter = Max_iter
        self.lb = lb
        self.ub = ub
        self.dim = dim
        self.SearchAgents_no = SearchAgents_no


        if carbon == True:
            self.legend = 'Carbon-GWO'
        else:
            self.legend = 'GWO'

        self.scheduler = TaskDeviceScheduler(self.devices, self.tasks, self.infrastructure, self.applications,
                                             self.lb, self.ub, self.dim, self.SearchAgents_no, self.Max_iter,carbon)

        super().__init__(infrastructure, applications, self.scheduler)
