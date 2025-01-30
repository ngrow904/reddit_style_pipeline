from cost_controller import CostController

# ✅ Initialize Cost Controller with logging enabled
controller = CostController(initial_budget=100.0)

# ✅ Example tasks to log costs
tasks = ["llm_call_small", "llm_call_medium", "scrape_api_call", "sd_generation"]

# ✅ Process tasks
for task in tasks:
    if controller.can_afford(task):
        print(f"✅ Running {task}, estimated cost: £{controller.estimate_cost(task)}")
        controller.log_cost(task)
    else:
        print(f"❌ Cannot afford {task}. Remaining budget: £{controller.monthly_budget:.2f}")

# ✅ Display remaining budget
print(f"Remaining monthly budget: £{controller.monthly_budget:.2f}")

# ✅ Notify user that logs are stored
print('Cost logs saved to data/cost_log.csv')
