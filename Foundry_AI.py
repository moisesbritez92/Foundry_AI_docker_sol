import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.ai.agents.models import ListSortOrder
from azure.core.exceptions import HttpResponseError

endpoint = "https://foundryproject-tecnun-resource.services.ai.azure.com/api/projects/foundryproject-tecnun"
agent_id = "asst_l7K5YHdGNfxlERMhAmwzDuhv"

azure_client_id = os.getenv("AZURE_CLIENT_ID")
azure_tenant_id = os.getenv("AZURE_TENANT_ID")
azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")

if azure_client_id and azure_tenant_id and azure_client_secret:
    print("Using ClientSecretCredential")
    credential = ClientSecretCredential(tenant_id=azure_tenant_id, client_id=azure_client_id, client_secret=azure_client_secret)
else:
    print("Using DefaultAzureCredential")
    credential = DefaultAzureCredential()

print(f"Connecting to: {endpoint}")
project = AIProjectClient(credential=credential, endpoint=endpoint)
agent = project.agents.get_agent(agent_id)
print(f"Connected to agent: {agent.id}\n")

thread = project.agents.threads.create()
print(f"Thread: {thread.id}\n=== Chat (escribe 'exit' para salir) ===\n")

try:
    while True:
        user_input = input("You: ").strip()
        if not user_input or user_input.lower() in ("exit", "quit"):
            break
        project.agents.messages.create(thread_id=thread.id, role="user", content=user_input)
        run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        if run.status == "failed":
            print(f"Error: {run.last_error}")
            continue
        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        for msg in messages:
            if msg.text_messages and msg.role == "assistant":
                print(f"assistant: {msg.text_messages[-1].text.value}\n---")
                break
except (KeyboardInterrupt, EOFError):
    print("\nSaliendo...")
