#!/usr/bin/env python3
"""
Trading Strategy Critic - Standalone Evaluation Tool

This script evaluates trading strategies against user requirements using
multiple AI models (GPT-4.1, Gemini 2.5 Pro, DeepSeek v3.1).
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Critic system prompt - defines the evaluation protocol
CRITIC_SYSTEM_PROMPT = """You are a critic agent. Your job is to check if a proposed trading strategy matches the user's original request.

## Your Task
1. Analyze whether the strategy correctly and fully addresses the user request.
2. If it does, explain briefly why.
3. If it does not, point out the specific gaps, mistakes, or mismatches.
4. Be strict: even small missing requirements should be flagged.

CRITICAL: Provide your reasoning first, then end your response with ONLY "Yes" or "No" on the last line. DO NOT use JSON format."""

# Critic user prompt template
CRITIC_PROMPT = """## User Request (Prompt)
{prompt}

## Generated Strategy
{strategy_output}

## Code
{code}
"""

# Available critic models
CRITIC_MODEL_LIST = {
    "gemini": "google/gemini-2.5-pro",
    "openai": "openai/gpt-4.1",
    "deepseek": "deepseek/deepseek-chat-v3.1",
}


def generate_critic(
    client: OpenAI,
    model_choice: str,
    user_prompt: str,
    strategy_output: str,
    code: str
) -> tuple[str, str]:
    """
    Generates a critique of the strategy using the specified model.

    Args:
        client: OpenAI client instance
        model_choice: Name of the model to use (gemini, openai, deepseek)
        user_prompt: The original user request
        strategy_output: The generated strategy configuration/description
        code: The generated Python code

    Returns:
        tuple: (critique_text, model_name)
    """
    model = CRITIC_MODEL_LIST.get(model_choice.lower())
    if not model:
        return f"Error: Unknown model '{model_choice}'", model_choice

    print(f"\n{'='*80}")
    print(f"Getting critique from {model_choice.upper()} ({model})...")
    print(f"{'='*80}\n")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": CRITIC_PROMPT.format(
                        prompt=user_prompt,
                        strategy_output=strategy_output,
                        code=code
                    )
                },
            ],
            max_completion_tokens=2000 if model_choice != "openai" else 10000,
            temperature=0.3
        )
        critique = response.choices[0].message.content
        return critique, model
    except Exception as e:
        error_msg = f"Error during API call to {model_choice}: {e}"
        print(f"! {error_msg}\n")
        return error_msg, model


def format_critique_output(critique: str, model: str) -> None:
    """Pretty print a critique with model information."""
    lines = critique.strip().split('\n')
    verdict = lines[-1].strip() if lines else "Unknown"

    # Color coding for terminal output
    verdict_color = '\033[92m' if verdict.lower() == 'yes' else '\033[91m'
    reset_color = '\033[0m'

    print(f"Model: {model}")
    print(f"Verdict: {verdict_color}{verdict}{reset_color}")
    print(f"\nReasoning:")
    print('-' * 80)
    print('\n'.join(lines[:-1]))
    print('-' * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate trading strategies using AI model critics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate with all three models
  python critic_standalone.py \\
    --prompt "Create a simple SMA crossover strategy" \\
    --strategy-output '{"timeframe": "1h", "indicators": ["SMA50", "SMA200"]}' \\
    --code "$(cat strategy.py)"

  # Evaluate with specific models only
  python critic_standalone.py \\
    --prompt "Your request here" \\
    --strategy-output "Your config here" \\
    --code "Your code here" \\
    --models gemini deepseek
        """
    )

    parser.add_argument(
        '--prompt',
        required=True,
        help='The original user request/prompt for the trading strategy'
    )

    parser.add_argument(
        '--strategy-output',
        required=True,
        help='The generated strategy configuration or description'
    )

    parser.add_argument(
        '--code',
        required=True,
        help='The generated Python strategy code'
    )

    parser.add_argument(
        '--models',
        nargs='+',
        choices=list(CRITIC_MODEL_LIST.keys()),
        default=list(CRITIC_MODEL_LIST.keys()),
        help='Which critic models to use (default: all)'
    )

    parser.add_argument(
        '--api-key',
        help='OpenRouter API key (overrides .env file)'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("OPENROUTER_CRITIC_API_KEY")
    if not api_key:
        print("Error: No API key provided!", file=sys.stderr)
        print("Either set OPENROUTER_CRITIC_API_KEY in .env or use --api-key", file=sys.stderr)
        sys.exit(1)
    print(api_key)

    # Initialize OpenAI client with OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    print(f"\n{'='*80}")
    print(f"TRADING STRATEGY EVALUATION")
    print(f"{'='*80}")
    print(f"\nUser Prompt:\n{args.prompt}\n")
    print(f"Evaluating with models: {', '.join(args.models)}\n")

    # Collect all critiques
    results = []
    for model_choice in args.models:
        critique, model = generate_critic(
            client,
            model_choice,
            args.prompt,
            args.strategy_output,
            args.code
        )
        results.append((critique, model, model_choice))
        format_critique_output(critique, model)
        print()

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    verdicts = []
    for critique, model, model_choice in results:
        lines = critique.strip().split('\n')
        verdict = lines[-1].strip() if lines else "Error"
        verdicts.append(verdict)
        print(f"{model_choice.upper():12} ({model:40}): {verdict}")

    # Consensus
    yes_count = sum(1 for v in verdicts if v.lower() == 'yes')
    no_count = sum(1 for v in verdicts if v.lower() == 'no')

    print(f"\nConsensus: {yes_count}/{len(verdicts)} models approved the strategy")

    if yes_count == len(verdicts):
        print("✓ All models agree: Strategy correctly implements the requirements")
    elif no_count == len(verdicts):
        print("✗ All models agree: Strategy has issues and needs revision")
    else:
        print("⚠ Mixed results: Review individual critiques for details")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
