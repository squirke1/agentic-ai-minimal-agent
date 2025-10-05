#!/usr/bin/env python3

"""
Interactive demo showing the agent solving your calculation task
"""

from tools import call_tool, get_vector_memory
import json

def solve_calculation_task():
    task = "Calculate 15 * 23 and tell me what this number represents in terms of days"
    print(f"Agent Task: {task}\n")
    
    # Step 1: Search memory for relevant experience
    print("Step 1: Searching long-term memory...")
    vector_memory = get_vector_memory()
    if vector_memory:
        memories = vector_memory.search_memories("calculation days", n_results=2)
        print(f"   Found {len(memories)} relevant memories")
    
    # Step 2: Use calculator tool
    print("\nStep 2: Using calculator...")
    calc_result = call_tool("calculator", '{"expression": "15 * 23"}')
    calc_data = json.loads(calc_result)
    
    if calc_data.get('ok'):
        result = calc_data['result']
        print(f"   15 × 23 = {result}")
        
        # Step 3: Analyze the result in terms of days
        print(f"\nStep 3: Analyzing {result} days...")
        
        # Calculate different time periods
        weeks_calc = call_tool("calculator", f'{{"expression": "{result} / 7"}}')
        weeks_data = json.loads(weeks_calc)
        
        months_calc = call_tool("calculator", f'{{"expression": "{result} / 30.44"}}')  # Average days per month
        months_data = json.loads(months_calc)
        
        years_calc = call_tool("calculator", f'{{"expression": "{result} / 365.25"}}')  # Including leap years
        years_data = json.loads(years_calc)
        
        print(f"   {result} days equals:")
        if weeks_data.get('ok'):
            print(f"   • {weeks_data['result']:.1f} weeks")
        if months_data.get('ok'):
            print(f"   • {months_data['result']:.1f} months")
        if years_data.get('ok'):
            print(f"   • {years_data['result']:.2f} years")
    
    # Step 4: Generate final response
    print("\nStep 4: Generating final response...")
    
    response = f"""
Calculation Result: 15 × 23 = {result}

What {result} days represents:

Time Periods:
- {weeks_data['result']:.1f} weeks (about {int(weeks_data['result'])} full weeks)
- {months_data['result']:.1f} months (roughly {int(months_data['result']+0.5)} months)
- {years_data['result']:.2f} years (just over 1 year)

Practical Context:
- Approximately 11 months and 2 weeks
- About {int((result/365.25)*100)}% of a full year

Real-world examples:
- Duration of a typical academic year
- Length of many professional training programs
- Time for a major life transition or goal achievement
    """
    
    print("\n=== FINAL ANSWER ===")
    print(response)
    
    # Step 5: Store experience in memory
    if vector_memory:
        print("\nStep 5: Storing experience...")
        experience = f"Calculated 15 × 23 = {result}. Explained that {result} days equals {weeks_data['result']:.1f} weeks, {months_data['result']:.1f} months, or {years_data['result']:.2f} years."
        memory_id = vector_memory.store_memory(
            content=experience,
            memory_type="experience", 
            importance=0.7,
            metadata={"calculation": True, "time_conversion": True}
        )
        print(f"   Stored as memory: {memory_id}")

if __name__ == "__main__":
    solve_calculation_task()