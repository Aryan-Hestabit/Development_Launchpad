import asyncio
import json
from orchestrator.planner import planner_agent
from agents.worker_agent import create_worker # Same factory as before
from agents.reflection_agent import reflection_agent
from agents.validator import validator_agent
from autogen_agentchat.messages import TextMessage

async def main():
    while True:
        user_query = input("USER: ")
        if user_query == "":
            continue
        elif user_query.lower() in ["exit", "quit"]:
            break
        else:
            # Dynamic Planning
            print("Planner is deciding how many workers to hire...")
            plan_res = await planner_agent.on_messages([TextMessage(content=user_query, source="user")], None)
            print(f"\n{plan_res}\n")
            print(f"Planner's response:\n{plan_res.chat_message.content}")
            
            # Parse the JSON plan
            try:
                tasks_list = json.loads(plan_res.chat_message.content)
            except:
                # Fallback if LLM fails JSON format
                tasks_list = [{"id": 1, "Role": "Generalist", "task": plan_res.chat_message.content}]
            
            # Worker Agent Creation
            print(f"Hiring {len(tasks_list)} specialized workers dynamically...")
            worker_agents = []
            execution_tasks = []

            for item in tasks_list:
                new_worker = create_worker(item['id'], item['Role'])
                worker_agents.append(new_worker)
                
                execution_tasks.append(
                    new_worker.on_messages([TextMessage(content=item['task'], source="planner")], None)
                )

            # 3. PARALLEL EXECUTION
            print("Running all workers in parallel...")
            results = await asyncio.gather(*execution_tasks)

            # 4. CONSOLIDATION & VALIDATION
            combined_report = "\n".join([f"REPORT BY {w.name}:\n{r.chat_message.content}" 
                                        for w, r in zip(worker_agents, results)])
            
            # 3. REFLECT (The "Critic" Phase)
            print("Reflection Agent is reviewing the work...")
            reflection_res = await reflection_agent.on_messages(
                [TextMessage(content=f"Original Plan: {plan_res}\n\nWorker Results: {combined_report}", source="system")], 
                None
            )
            critique = reflection_res.chat_message.content
            print(f"CRITIQUE:\n{critique}\n")

            print("Validator is finalizing the report... \n\n")
            final_output = await validator_agent.on_messages([TextMessage(content=f"query: {user_query} context: {combined_report}", source="system")], None)
            
            print(f"\nFINAL ANSWER:\n\n{final_output.chat_message.content}")

if __name__ == "__main__":
    asyncio.run(main())