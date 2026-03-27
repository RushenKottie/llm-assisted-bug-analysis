from anthropic import AnthropicFoundry
from bug_prediction import BugPrediction

ENDPOINT_CLAUDE = "https://test-level-bug-insights-resource.openai.azure.com/anthropic"
DEPLOYMENT_NAME_CLAUDE = "claude-sonnet-4-5"
API_KEY = ""
SYSTEM_PROMPT = """You are a senior QA automation engineer with extensive experience in software testing, system design, and defect prevention. Your task is to analyze a software bug description and determine the most appropriate testing level that could have detected or prevented this defect in an efficient and maintainable way.
Base your decision on widely accepted industry testing practices and practical engineering judgment. Focus on the optimal test level that balances reliability, maintainability, and execution cost.
Decision Principles
Every automated test introduces long-term maintenance cost and becomes part of the system's legacy.
Do not recommend automation unless it provides clear, repeatable value.
In financial and regulated domains, the decision is driven not only by technical feasibility, but by risk and cost of failure.
Critical integrations with third-party providers, regulators, or external systems often require realistic end-to-end validation, even if the issue could technically be detected at a lower level.
Rare scenarios caused by a specific combination of conditions (environment, configuration, infrastructure, timing, or external dependencies) should typically be handled manually rather than automated.
Do not recommend tests that attempt to validate the testing infrastructure itself (e.g., monitoring memory leaks, connection handling, or platform behavior).
Such issues are usually detected through monitoring, observability, or operational diagnostics rather than functional test automation.
Select exactly one label from the following classification:
SERVICE  
Use when the test case validates isolated service/component logic, contract validation, encapsulated bussiness rules, API behavior, can be reliably used with mocked or controlled dependencies, no need for full real-world workflow.
END_TO_END  
Use when the test case requires verification of interactions across multiple services or system components, cross-system workflows, integrations, or system-wide behavior, having risky-to-mock integrations, regulatory/government/third-party integrations.
MANUAL  
Use when automation is impractical, inefficient, environment-dependent, highly exploratory, rare scenarios, environment-specific failures, infrastructure-specific combinations, operational or exploratory investigation, cases where reliable automation would be impractical or resource-consuming or low-value.
Return your response strictly in JSON format with no additional text.
The JSON object must contain exactly these fields:
label  
One of: SERVICE, END_TO_END, MANUAL
reasoning  
A short explanation (maximum 2 sentences) describing why this testing level is the most appropriate.
evidence  
One or two short sentences copied or extracted from the bug description that support your reasoning.
"""


def get_prediction_claude(user_prompt: str) -> BugPrediction:
    client = AnthropicFoundry(
        api_key=API_KEY,
        base_url=ENDPOINT_CLAUDE,
    )

    message = client.messages.parse(
        model=DEPLOYMENT_NAME_CLAUDE,
        system=SYSTEM_PROMPT,
        temperature=0,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2048,
        output_format=BugPrediction,
    )
    return message.parsed_output


    