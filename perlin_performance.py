""" Creates a Performance.csv of statistics for perlin_noise.py and perlin_noise_parallel.py """
import timeit
import csv

# Noise Scale
scale = 10
# Times to repeat the same test for more accurate average
repeat = 5
# Max processes to use for parallel algorithm
max_cpu = 8


# Write to csv
with open("Performance.csv", 'w') as csvfile:
    # Test column is name of algorithm and noise dimensions
    fieldnames = ["Test"]
    # Add a column for each cpu used in test
    fieldnames.extend([f"CPU_{n}" for n in range(1, max_cpu+1)])
    
    # Writer converts dicts to spreasheet rows
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Dimensions are 2**x, ex: 2**9=512, dimensions will be 512x512 for all tests
    for x in range(6, 14):
        # Set width and height to same dimmension
        width = 2**x
        height=width

        # Perform sequential test of original algorithm
        time_sequential = timeit.timeit(f"perlin_noise.generate_perlin_noise({width}, {height}, {scale})", setup="import perlin_noise", number=repeat)
        # total time spent must be divided by repeat amount to get average time spent
        time = time_sequential/repeat
        # Set test name (VitoshAcademy is name of py code creator)
        row = {"Test": f"Vitosh {width} x {height}"}
        # Set all cpus to the same time found (this code is non parallel)
        for cpu in range(1, max_cpu+1):
            row[f"CPU_{cpu}"]= f"{time}"
        # Write the row
        writer.writerow(row)
        # Notify user of row written
        print(row)

        # New row of parallel algorithm
        row = {"Test": f"Parallel {width} x {height}"}
        # Run test for each cpu from 1 to max
        for cpu in range(1, max_cpu+1):
            # Run noise generation of parallel algorithm
            time_paral  = timeit.timeit(f"perlin_noise_parallel.generate_perlin_noise({width}, {height}, {scale}, {cpu})", setup="import perlin_noise_parallel", number=repeat)
            # Get average from repeated test
            time = time_paral / repeat
            # Update dictionary for this test
            row[f"CPU_{cpu}"] = f"{time}"

        # Write parallel test to csv
        writer.writerow(row)
        # Notify user test is done
        print(row)
