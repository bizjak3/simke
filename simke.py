"""Minimal jobshop example."""
import collections
from ortools.sat.python import cp_model


def main():
    """Minimal jobshop problem."""
    # Data.
    jobs_data = [  # task = (machine_id, processing_time).
        [(10,10)],  # 12947
        [(0,10),(11,30)], #13620
        [(0,10),(11,5)], #13621
        [(4,6),(7,20),(6,35)], #13953
        [(4,12),(7,25)], #13962
        [(7,25),(6,37)], #13963
        [(2,20),(10,10)], #33863
        [(7,2)], #34257
        [(2,10),(10,20)], #34602
        [(4,25),(2,5)], #34603
        [(7,3)], #36215
        [(6,35),(7,7)], # 36216
        [(7,7),(6,20)], #36217
        [(7,3)], #36218
        [(3,17),(6,30),(8,10),(9,35),(10,10)], #37871
        [(0,10),(11,2)], #37873
        [(4,10),(2,50),(6,5)], #37874
        [(1,400)],#37876
        [(1,500)], #37876
        [(4,30),(6,35)], #37877
        [(0,18),(6,30),(11,24)], #53379
        [(1,620)], #53380
        [(0,25),(3,5),(8,10),(9,15),(11,60)], #53381
        [(3,25)], #53389
        [(3,5),(6,10),(10,5)], #53840
        [(4,5)], #53841
        [(4,10)], #53842
        [(5,10)], #53843
        [(2,10)], #53998
        [(2,10)], #53999
        [(2,20),(10,30)], #54000
        [(7,4)], #54001
        [(3,13),(6,15),(10,12)], #54338
        [(3,13),(6,40),(8,20),(9,70),(10,16)], #54339
        [(2,45),(10,20)], #54341
        [(3,55),(6,125),(8,20),(9,80),(11,20)], #54673
        [(8,20),(9,80),(11,60)], #54674
        [(0,10),(11,2)], #54675
        [(3,10),(5,30),(10,20)], #54678
        [(4,10),(2,10)], #55467
        [(0,2),(2,5)], #55468
        [(0,2),(2,5)], #55469
        [(7,4),(8,20),(9,70),(11,60)], #56498
        [(3,5),(6,20),(10,10)], #57775
        [(3,7),(6,60),(10,30)] #57776

        # [(10,10)],  # 12947
        # [(0,10),(11,30)], #13620
        # [(0,10),(11,5)], #13621
        # [(4,6),(7,20),(6,35)], #13953
        # [(4,12),(7,25)], #13962
        # [(7,25),(6,37)], #13963
        # [(2,20),(10,10)], #33863
        # [(7,2)], #34257
        # [(2,10),(10,20)], #34602
        # [(4,25),(2,5)], #34603
        # [(7,3)], #36215
        # [(6,35),(7,7)], # 36216
        # [(7,7),(6,20)], #36217
        # [(7,3)], #36218
        # [(3,17),(6,30),(9,35),(10,10)], #37871
        # [(0,10),(11,2)], #37873
        # [(4,10),(2,50),(6,5)], #37874
        # [(1,400)],#37876
        # [(1,500)], #37876
        # [(4,30),(6,35)], #37877
        # [(0,18),(6,30),(11,24)], #53379
        # [(1,620)], #53380
        # [(0,25),(3,5),(9,15),(11,60)], #53381
        # [(3,25)], #53389
        # [(3,5),(6,10),(10,5)], #53840
        # [(4,5)], #53841
        # [(4,10)], #53842
        # [(5,10)], #53843
        # [(2,10)], #53998
        # [(2,10)], #53999
        # [(2,20),(10,30)], #54000
        # [(7,4)], #54001
        # [(3,13),(6,15),(10,12)], #54338
        # [(3,13),(6,40),(9,70),(10,16)], #54339
        # [(2,45),(10,20)], #54341
        # [(3,55),(6,125),(9,80),(11,20)], #54673
        # [(9,80),(11,60)], #54674
        # [(0,10),(11,2)], #54675
        # [(3,10),(5,30),(10,20)], #54678
        # [(4,10),(2,10)], #55467
        # [(0,2),(2,5)], #55468
        # [(0,2),(2,5)], #55469
        # [(7,4),(9,70),(11,60)], #56498
        # [(3,5),(6,20),(10,10)], #57775
        # [(3,7),(6,60),(10,30)] #57776 
    ]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            duration = task[1]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(start=start_var,
                                                   end=end_var,
                                                   interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            if task_id != 8:
                model.Add(all_tasks[job_id, task_id +
                                    1].start >= all_tasks[job_id, task_id].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        all_tasks[job_id, len(job) - 1].end
        for job_id, job in enumerate(jobs_data)
    ])
    model.Minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution:')
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(start=solver.Value(
                        all_tasks[job_id, task_id].start),
                                       job=job_id,
                                       index=task_id,
                                       duration=task[1]))

        # Create per machine output lines.
        output = ''
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = 'Machine ' + str(machine) + ': '
            sol_line = '           '

            for assigned_task in assigned_jobs[machine]:
                name = 'job_%i_task_%i' % (assigned_task.job,
                                           assigned_task.index)
                # Add spaces to output to align columns.
                sol_line_tasks += '%-15s' % name

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = '[%i,%i]' % (start, start + duration)
                # Add spaces to output to align columns.
                sol_line += '%-15s' % sol_tmp

            sol_line += '\n'
            sol_line_tasks += '\n'
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print("this:")
        print(solver.SearchForAllSolutions)
        print(f'Optimal Schedule Length: {solver.ObjectiveValue()}')
        print(output)
    else:
        print('No solution found.')

    # Statistics.
    print('\nStatistics')
    print('  - conflicts: %i' % solver.NumConflicts())
    print('  - branches : %i' % solver.NumBranches())
    print('  - wall time: %f s' % solver.WallTime())


if __name__ == '__main__':
    main()