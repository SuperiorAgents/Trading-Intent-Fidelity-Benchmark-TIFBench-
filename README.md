# Trading Intent Fidelity Benchmark (TIFbench)

An automated evaluation tool that uses multiple leading AI models to critique and validate trading strategy implementations against natural language requirements.

## Overview

This tool helps evaluate whether a generated trading strategy (code + configuration) correctly implements the requirements from a user's original prompt. You can either:

1. **Manual Evaluation**: Review the outputs yourself as a human evaluator
2. **Automated Evaluation**: Use three state-of-the-art AI models (GPT-4.1, Gemini 2.5 Pro, and DeepSeek v3.1) to automatically critique the implementation

The critics analyze:
- Whether the strategy correctly addresses all user requirements
- Missing features or incomplete implementations
- Mismatches between the request and the generated code
- Technical correctness of the trading logic

## Setup

### Prerequisites
- Python 3.12+
- An OpenRouter API key (for automated evaluation)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SuperiorAgents/Trading-Intent-Fidelity-Benchmark-TIFBench-.git
cd Trading-Intent-Fidelity-Benchmark-TIFBench-

# 2. Create and activate a Python virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install openai python-dotenv

# 4. Set up your API key (for automated evaluation only)
cp .env.example .env
# Edit .env and add your OpenRouter API key:
# OPENROUTER_CRITIC_API_KEY=your_api_key_here
```

## Usage

### Option 1: Manual Evaluation

Simply review the three inputs yourself:

1. **User Prompt**: The original natural language request
2. **Strategy Output**: The JSON configuration generated
3. **Code**: The Python strategy implementation

Ask yourself: "Does this code and configuration fully and correctly implement what was requested?"

### Option 2: Automated Evaluation

Run the critic script to get feedback from three AI models:

```bash
python critic.py \
  --prompt "Your original user request here" \
  --strategy-output "Generated strategy JSON/description" \
  --code "Generated Python code" \
  --models gemini openai deepseek
```

**Arguments:**
- `--prompt`: The original natural language request for the trading strategy
- `--strategy-output`: The generated strategy description or configuration (can be JSON or text)
- `--code`: The generated Python strategy code
- `--models`: Which models to use for evaluation (options: `gemini`, `openai`, `deepseek`)
  - You can specify one or more models
  - Default: all three models

**Example:**

```bash
python critic.py \
  --prompt "Create a simple moving average crossover strategy using 50 and 200 period SMAs" \
  --strategy-output '{"timeframe": "1h", "indicators": ["SMA50", "SMA200"]}' \
  --code "$(cat my_strategy.py)" \
  --models gemini openai
```

### Output Format

Each critic model will provide:
1. **Reasoning**: Detailed analysis of how well the strategy matches the request
2. **Verdict**: A final "Yes" or "No" on the last line
   - **Yes**: The strategy correctly implements the request
   - **No**: There are issues, gaps, or mismatches

## How It Works

The critic models use a strict evaluation protocol:

1. Analyze whether the strategy correctly and fully addresses the user request
2. Check for completeness - even small missing requirements are flagged
3. Identify specific gaps, mistakes, or mismatches
4. Provide detailed reasoning followed by a binary verdict

## Model Selection

The tool uses three different models to provide diverse perspectives:

- **Gemini 2.5 Pro** (`google/gemini-2.5-pro`): Google's latest reasoning model
- **GPT-4.1** (`openai/gpt-4.1`): OpenAI's advanced language model
- **DeepSeek v3.1** (`deepseek/deepseek-chat-v3.1`): Specialized reasoning model

You can use any combination of these models based on your needs and budget.

## Use Cases

- **Strategy Generation Validation**: Verify that AI-generated trading strategies match requirements
- **Code Review**: Get automated feedback on trading strategy implementations
- **Requirement Verification**: Ensure all requested features are properly implemented
- **Quality Assurance**: Multi-model consensus for higher confidence evaluations
- **Educational**: Learn what makes a good trading strategy implementation

## Configuration

The critic evaluation parameters can be adjusted in the script:

- `temperature`: Controls randomness (default: 0.3 for consistent, focused critiques)
- `max_tokens`: Maximum response length (default: 2000-10000 depending on model)

## API Costs

Using the automated evaluation feature requires OpenRouter API credits. Costs vary by model:
- Gemini 2.5 Pro: ~$0.01-0.02 per evaluation
- GPT-4.1: ~$0.03-0.05 per evaluation
- DeepSeek v3.1: ~$0.001-0.002 per evaluation

Prices are approximate and may change. Check [OpenRouter pricing](https://openrouter.ai/) for current rates.
