import matplotlib.pyplot as plt
import numpy as np


def plot_task_iterations(task_lists, iteration_lists, labels, colors, width=0.2):
    """
    Plot a bar chart with 'number of tasks' on the X-axis and 'iteration number' on the Y-axis,
    with bars placed side by side, using arrays instead of DataFrames.

    Parameters:
    task_lists (list of lists): A list of arrays/lists, each containing 'number of tasks' values.
    iteration_lists (list of lists): A list of arrays/lists, each containing 'iteration number' values.
    labels (list of str): List of labels for each dataset to be used in the legend.
    colors (list of str): List of colors for each dataset bar plot.
    width (float): Width of each bar (default is 0.2).
    """
    plt.figure(figsize=(10, 6))

    # Extract the 'number of tasks' from the first list (assuming all have the same tasks)
    num_tasks = task_lists[0]

    # Determine the number of datasets and the indices
    num_dataframes = len(task_lists)
    indices = np.arange(len(num_tasks))  # Get the indices for each bar group

    # Loop over the datasets and plot each one with an offset
    for i in range(num_dataframes):
        # Offset each bar group by i * width
        plt.bar(indices + i * width, iteration_lists[i],
                width=width, label=labels[i], color=colors[i], alpha=0.7)

    # Customize the plot
    plt.xlabel('Number of Tasks')
    plt.ylabel('Iteration Number')
    plt.title('Bar Plot for Multiple Files (Side by Side)')
    plt.xticks(indices + width * (num_dataframes - 1) / 2, num_tasks)  # Adjust X-axis tick positions
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()


# Example of how to call the function with arrays
# Example arrays (replace these with your actual data)
tasks = [1, 2, 3,4,5,6,7,8]
iterations1 = [5, 10, 15,17,22,26,28,30]
iterations2 = [6, 12, 18,25,30,31,32,33]
iterations3 = [7, 14, 21,26,27,28,29,30]
iterations4 = [8, 16, 24,30,33,34,34,35]

# Call the plotting method with arrays
plot_task_iterations([tasks, tasks, tasks, tasks],  # Task lists (assuming same tasks)
                     [iterations1, iterations2, iterations3, iterations4],  # Iteration lists
                     labels=['File 1', 'File 2', 'File 3', 'File 4'],  # Labels
                     colors=['blue', 'green', 'red', 'orange'],  # Colors
                     width=0.2)  # Bar width
