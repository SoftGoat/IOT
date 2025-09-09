import csv

def log_simulation_results(n_pass, n_doors, mean_sp, brate, dwell_time, filename='simulation_log.csv'):
    with open(filename, 'a', newline='') as csvfile:
        csv.writer(csvfile).writerow([n_pass, n_doors, mean_sp, brate, dwell_time])
