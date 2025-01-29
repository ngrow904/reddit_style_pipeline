from cost_controller import CostController

# Initialize a Cost Controller with a £100 budget
controller = CostController(monthly_budget=100.0)

# Example tasks
tasks = ["llm_call_small", "llm_call_medium", "scrape_api_call", "sd_generation"]

# Check if we can afford each task and log the cost
for task in tasks:
    if controller.can_afford(task):
        print(f"✅ Running {task}, estimated cost: £{controller.estimate_cost(task)}")
        controller.log_cost(task)
    else:
        print(f"❌ Cannot afford {task}, remaining budget: £{controller.get_remaining_budget()}")

# Display remaining budget
print(f"Remaining monthly budget: £{controller.get_remaining_budget()}")
