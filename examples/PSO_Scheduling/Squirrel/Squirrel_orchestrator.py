from examples.PSO_Scheduling.comparing_orchestrator import comparing_orchestrator
from examples.PSO_Scheduling.Squirrel.Squirrel import TaskDeviceScheduler
from examples.PSO_Scheduling.Squirrel.Squirrel_Carbon import TaskDeviceScheduler as carbonTaskDeviceScheduler

class SquirrelOrchestrator(comparing_orchestrator):
    def __init__(self, devices, tasks, infrastructure, applications, bounds, num_squirrels, max_iter, gl, pc, pd,carbon=False):
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
            self.scheduler= carbonTaskDeviceScheduler(devices, tasks, infrastructure, applications,bounds, num_squirrels, max_iter, gl, pc, pd)
        else:
            self.legend = 'Squirell'
            self.scheduler = TaskDeviceScheduler(devices, tasks, infrastructure, applications,bounds, num_squirrels, max_iter, gl, pc, pd)

        super().__init__(infrastructure, applications, self.scheduler)