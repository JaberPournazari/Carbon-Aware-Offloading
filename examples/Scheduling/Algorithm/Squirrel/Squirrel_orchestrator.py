from examples.Scheduling.comparing_orchestrator import comparing_orchestrator
from examples.Scheduling.Algorithm.Squirrel.Squirrel import TaskDeviceScheduler

class SquirrelOrchestrator(comparing_orchestrator):
    def __init__(self,  infrastructure, applications, devices, tasks, bounds, num_squirrels, max_iter, gl, pc, pd,carbon=False):
        self.devices = devices
        self.tasks = tasks
        self.infrastructure = infrastructure
        self.applications = applications
        self.Max_iter = max_iter
        self.bounds=bounds
        self.num_squirrels=num_squirrels
        self.gl = gl
        self.pc = pc
        self.pd = pd

        if carbon == True:
            self.legend = 'Carbon-Squirell'
        else:
            self.legend = 'Squirell'

        self.scheduler = TaskDeviceScheduler(devices, tasks, infrastructure, applications,bounds, num_squirrels, max_iter, gl, pc, pd,carbon)

        super().__init__(infrastructure, applications, self.scheduler)