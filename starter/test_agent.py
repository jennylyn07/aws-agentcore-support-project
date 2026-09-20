"""
Test script to invoke the deployed customer_support_agent directly via boto3.
Bypasses agentcore CLI's Windows argument-quoting bug.

Usage:
    python test_agent.py "Your prompt here" CUST-123 session-id-1
"""
import boto3
import json
import sys

AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:722653222021:runtime/customer_support_agent-ihjX1kEs2A"
REGION = "us-east-1"

def invoke(prompt: str, customer_id: str, session_id: str):
    client = boto3.client("bedrock-agentcore", region_name=REGION)

    payload = json.dumps({
        "prompt": prompt,
        "customer_id": customer_id,
        "session_id": session_id,
    }).encode()

    # runtimeSessionId (the AWS API-level session) must be >= 33 characters.
    # Pad our short, human-readable session_id to meet that requirement while
    # keeping it deterministic (same session_id -> same runtime session).
    runtime_session_id = (session_id + "-" + "x" * 40)[:40].ljust(33, "0")

    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=runtime_session_id,
        payload=payload,
    )

    content_type = response.get("contentType", "")

    if "text/event-stream" in content_type:
        lines = []
        for line in response["response"].iter_lines(chunk_size=10):
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    decoded = decoded[6:]
                lines.append(decoded)
        result = "\n".join(lines)
        print(result)
        return result
    elif content_type == "application/json":
        chunks = [c.decode("utf-8") for c in response.get("response", [])]
        joined = "".join(chunks)
        try:
            parsed = json.loads(joined)
            print(json.dumps(parsed, indent=2))
            return parsed
        except json.JSONDecodeError:
            print(joined)
            return joined
    else:
        # Fallback: try reading raw bytes
        try:
            raw = response["response"].read()
            decoded = raw.decode("utf-8")
            print(decoded)
            return decoded
        except Exception as e:
            print("Raw response object:", response)
            print("Error decoding:", e)
            return None


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python test_agent.py \"<prompt>\" <customer_id> <session_id>")
        sys.exit(1)

    prompt = sys.argv[1]
    customer_id = sys.argv[2]
    session_id = sys.argv[3]

    print(f"--- Invoking agent ---")
    print(f"Prompt: {prompt}")
    print(f"Customer: {customer_id}  Session: {session_id}")
    print("---")
    invoke(prompt, customer_id, session_id)