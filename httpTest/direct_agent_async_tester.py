import asyncio
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as agent_main

async def run_agent(prompt: str):
    """
    Run the agent with the given prompt
    
    Args:
        prompt: The input prompt for the agent
    """
    # Modify sys.argv to simulate command-line arguments
    import sys
    original_argv = sys.argv.copy()  # Save original arguments
    
    # Set new arguments
    sys.argv = [sys.argv[0], '--prompt', prompt]
    
    # Run the agent
    try:
        await agent_main()
    finally:
        # Restore original arguments
        sys.argv = original_argv

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Directly test the agent')
    parser.add_argument('--prompt', type=str, required=True, 
                        help='The prompt for the agent')
    
    args = parser.parse_args()
    
    print(f"Running agent with prompt: '{args.prompt}'")
    print("="*50)
    
    # Run the async function
    asyncio.run(run_agent(args.prompt))
    
    print("="*50)
    print("Agent execution completed")