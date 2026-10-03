"""Which Bedrock model IDs this account can actually invoke on demand.
Run once before the experiment; records the substitutions noted in RESULTS.md."""
import boto3

br = boto3.client("bedrock-runtime", region_name="us-east-1")
IDS = [
    # as specified in the brief
    "anthropic.claude-haiku-4-5-20251001-v1:0",
    "anthropic.claude-sonnet-4-20250514-v1:0",
    "us.meta.llama3-1-70b-instruct-v1:0",
    "us.meta.llama3-3-70b-instruct-v1:0",
    "amazon.nova-pro-v1:0",
    # cross-region inference profiles actually used
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.mistral.pixtral-large-2502-v1:0",
]
for mid in IDS:
    try:
        r = br.converse(
            modelId=mid,
            messages=[{"role": "user", "content": [{"text": "Reply with the single word: ok"}]}],
            inferenceConfig={"maxTokens": 16, "temperature": 0.0},
        )
        print("OK    %-50s %r" % (mid, r["output"]["message"]["content"][0]["text"].strip()))
    except Exception as e:
        print("FAIL  %-50s %s: %s" % (mid, type(e).__name__, str(e)[:110]))
