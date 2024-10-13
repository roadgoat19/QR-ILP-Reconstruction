import tkinter as tk
from tkinter import simpledialog, scrolledtext
import pulp  # Ensure PuLP is installed
from directionalsums import SumCalculator
import io
import sys

class MatrixGUI:
    def __init__(self, master):
        self.master = master
        master.title("Matrix Directional Sums")

        self.size = 5
        self.sum_calc = SumCalculator(self.size)

        self.labels = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.draw_matrix()

        # Frame for buttons, using grid
        self.button_frame = tk.Frame(master)
        self.button_frame.grid(row=self.size, column=0, columnspan=self.size + 1, sticky="ew")

        # Button to compute all directional sums and display them
        self.compute_button = tk.Button(self.button_frame, text="Compute and Display All Directional Sums", command=self.compute_and_display_sums)
        self.compute_button.grid(row=0, column=0)

        # Button to adjust sums based on a known point
        self.adjust_button = tk.Button(self.button_frame, text="Adjust Directional Sums", command=self.adjust_sums)
        self.adjust_button.grid(row=0, column=1)

        # Button to solve ILP and display the solution
        self.solve_ilp_button = tk.Button(self.button_frame, text="Solve ILP and Display Solution", command=self.solve_ilp_and_display)
        self.solve_ilp_button.grid(row=0, column=2)

        # Text widget to display directional sums
        self.sums_display = scrolledtext.ScrolledText(master, width=40, height=20)
        self.sums_display.grid(row=0, column=self.size, rowspan=self.size, sticky="nsew")

        # Text widget to display ILP solution
        self.solution_display = scrolledtext.ScrolledText(master, width=40, height=20)
        self.solution_display.grid(row=0, column=self.size + 1, rowspan=self.size, sticky="nsew")

    def draw_matrix(self):
        for i in range(self.size):
            for j in range(self.size):
                self.labels[i][j] = tk.Label(self.master, text=str(self.sum_calc.matrix[i][j]), borderwidth=1, relief="solid", width=2, height=1)
                self.labels[i][j].grid(row=i, column=j, padx=1, pady=1)

    def compute_and_display_sums(self):
        self.sum_calc.computeAllDirectionalSums()
        self.display_directional_sums()

    def adjust_sums(self):
        x = simpledialog.askinteger("Input", "Enter the x coordinate of the known point:")
        y = simpledialog.askinteger("Input", "Enter the y coordinate of the known point:")
        if x is not None and y is not None:
            self.sum_calc.adjustDirectionalSums((x, y), self.sum_calc.matrix[x][y])
            self.display_directional_sums()

    def display_directional_sums(self):
        self.sums_display.delete('1.0', tk.END)  # Clear previous sums
        for key, value in self.sum_calc.sumLibrary.items():
            start, slope = key
            line, rowSum = value
            self.sums_display.insert(tk.END, f"Start: {start}, Slope: {slope}, Sum: {rowSum}\n")

    def solve_ilp_and_display(self):
        # Redirect stdout to capture the solver's output
        old_stdout = sys.stdout  # Save the current stdout to restore later
        sys.stdout = buffer = io.StringIO()

        # Call the ILP solver with the current sumLibrary
        solution_matrix = self.solve_ilp(self.sum_calc.sumLibrary, self.size)

        # Restore stdout
        sys.stdout = old_stdout
        solver_output = buffer.getvalue()

        # Display the solution and solver output in the solution_display Text widget
        self.solution_display.delete('1.0', tk.END)  # Clear previous solution
        if solution_matrix:
            for row in solution_matrix:
                self.solution_display.insert(tk.END, f"{row}\n")
            self.solution_display.insert(tk.END, "\nSolver Diagnostic Information:\n")
            self.solution_display.insert(tk.END, solver_output)
        else:
            self.solution_display.insert(tk.END, "No feasible solution found.\n")
            self.solution_display.insert(tk.END, "\nSolver Diagnostic Information:\n")
            self.solution_display.insert(tk.END, solver_output)


    def solve_ilp(self, sum_library, n):
        problem = pulp.LpProblem("MatrixReconstruction", pulp.LpMinimize)
        variables = pulp.LpVariable.dicts("Cell", (range(n), range(n)), cat='Binary')
        for key, value in sum_library.items():
            cells, required_sum = value
            problem += pulp.lpSum(variables[row][col] for row, col in cells) == required_sum, f"SumConstraint_{key}"
        problem += 0, "ArbitraryObjective"
        problem.solve()
        if pulp.LpStatus[problem.status] == 'Optimal':
            return [[variables[i][j].varValue for j in range(n)] for i in range(n)]
        return None

def main():
    root = tk.Tk()
    gui = MatrixGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()


