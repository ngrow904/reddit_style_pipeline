import csv
import os
import datetime

class CostController:
    def __init__(self, initial_budget=100.0, log_file='data/cost_log.csv', alert_threshold=20.0):
        """Initializes the Cost Controller with a running budget system that adds £100 every 15th."""        
        self.log_file = log_file
        self.budget_file = 'data/budget.txt'
        self.alert_threshold = alert_threshold

        # ✅ Ensure the 'data/' directory exists
        log_directory = os.path.dirname(self.log_file)
        if log_directory and not os.path.exists(log_directory):
            os.makedirs(log_directory, exist_ok=True)

        # ✅ Load existing budget or initialize
        self.monthly_budget = self.load_budget(initial_budget)

        # ✅ Add budget on the 15th if necessary
        self.check_and_add_budget()

        # ✅ Ensure log file exists with headers
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Date', 'Task', 'Cost', 'Remaining Budget', 'Warnings'])

    def load_budget(self, initial_budget):
        """Loads the last saved budget or initializes it if missing."""        
        if os.path.exists(self.budget_file):
            with open(self.budget_file, 'r') as file:
                return float(file.read().strip())
        return initial_budget

    def save_budget(self):
        """Saves the current budget to persist across runs."""        
        with open(self.budget_file, 'w') as file:
            file.write(str(self.monthly_budget))

    def estimate_cost(self, task_type):
        """Returns an estimated cost for a given task."""        
        cost_dict = {
            "llm_call_small": 0.01,
            "llm_call_medium": 0.05,
            "sd_generation": 0.02,
            "scrape_api_call": 0.005
        }
        return cost_dict.get(task_type, 0.01)

    def can_afford(self, task_type):
        """Checks if there is enough budget left for a task."""        
        estimated_cost = self.estimate_cost(task_type)
        return (self.monthly_budget - estimated_cost) >= 0

    def log_cost(self, task_type, actual_cost=None):
        """Logs the cost of a task, updates the spent amount, and triggers alerts if needed."""        
        if actual_cost is None:
            actual_cost = self.estimate_cost(task_type)

        if self.can_afford(task_type):
            self.monthly_budget -= actual_cost
            self.save_budget()

            warning_message = ""
            # ✅ Trigger alert if budget is below the threshold
            if self.monthly_budget < self.alert_threshold:
                warning_message = f"⚠️ Low budget! Only £{self.monthly_budget:.2f} remaining."
                print(warning_message)

            # ✅ Write to CSV log with warnings
            with open(self.log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.date.today(), task_type, actual_cost, self.monthly_budget, warning_message])
        else:
            print(f"❌ Cannot afford {task_type}. Remaining budget: £{self.monthly_budget:.2f}")

    def check_and_add_budget(self):
        """Adds £100 on the 15th of each month if needed."""        
        today = datetime.date.today()
        if today.day == 15:
            self.top_up_budget(100.0)

    def top_up_budget(self, amount):
        """Adds a specified amount to the budget."""        
        self.monthly_budget += amount
        self.save_budget()
        print(f"💰 Mid-month top-up: Added £{amount:.2f}. New budget: £{self.monthly_budget:.2f}")

        # ✅ Log the top-up in cost_log.csv
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([datetime.date.today(), "Mid-Month Top-Up", f"+{amount}", self.monthly_budget, ""])
