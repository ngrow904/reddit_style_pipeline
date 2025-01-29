class CostController:
    def __init__(self, monthly_budget=100.0):
        """
        Initializes the Cost Controller with a budget limit.
        :param monthly_budget: The maximum amount of money (in GBP) to spend per month.
        """
        self.monthly_budget = monthly_budget  # Set the max budget
        self.spent_so_far = 0.0  # Track total spent

    def estimate_cost(self, task_type):
        """
        Returns an estimated cost for a given task.
        :param task_type: The type of task (e.g., 'llm_call_small', 'scrape_api_call').
        :return: Estimated cost in GBP.
        """
        cost_dict = {
            "llm_call_small": 0.01,  # Small GPT-3.5 API call
            "llm_call_medium": 0.05,  # Larger LLM call
            "sd_generation": 0.02,  # Image generation (Stable Diffusion)
            "scrape_api_call": 0.005  # Web scraping API call
        }
        return cost_dict.get(task_type, 0.01)  # Default to 0.01 if unknown task

    def can_afford(self, task_type):
        """
        Checks if there is enough budget left for a task.
        :param task_type: The type of task to check.
        :return: True if affordable, False if not.
        """
        estimated_cost = self.estimate_cost(task_type)
        return (self.spent_so_far + estimated_cost) <= self.monthly_budget

    def log_cost(self, task_type, actual_cost=None):
        """
        Logs the cost of a task and updates the spent amount.
        :param task_type: The type of task performed.
        :param actual_cost: The actual cost, if available. Otherwise, uses estimate.
        """
        if actual_cost is None:
            actual_cost = self.estimate_cost(task_type)
        self.spent_so_far += actual_cost

    def get_remaining_budget(self):
        """
        Returns the remaining budget for the month.
        """
        return self.monthly_budget - self.spent_so_far
