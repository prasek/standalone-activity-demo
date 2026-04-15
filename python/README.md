# Standalone Activities Demo (Python)

A minimal working demo of [Temporal Standalone Activities](https://docs.temporal.io/standalone-activity) in Python, built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and the [Temporal Developer Skill](https://github.com/temporalio/skill-temporal-developer).

Standalone Activities let you execute durable activities directly from a client - no parent workflow required. Think of them as a durable, observable replacement for traditional job queues with built-in retries, timeouts, and lifecycle controls.

## What this demo does

- **`activities/greet.py`** - Defines a simple activity (`compose_greeting`) that takes a greeting and a name
- **`worker.py`** - Runs a worker that polls for standalone activity tasks
- **`starter.py`** - Executes standalone activities two ways:
  1. `client.execute_activity()` - start and wait for the result
  2. `client.start_activity()` - start without blocking, fetch the result later

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** - Python package manager
- **Temporal CLI (Standalone Activity pre-release)** - the standard CLI does not include SAA server support yet

### Install the Temporal CLI (SAA build)

Download the pre-release CLI that bundles a server with standalone activity support:

```bash
# macOS Apple Silicon
curl -L https://github.com/temporalio/cli/releases/download/v1.6.2-standalone-activity/temporal_cli_1.6.2-standalone-activity_darwin_arm64.tar.gz | tar xz

# macOS Intel
curl -L https://github.com/temporalio/cli/releases/download/v1.6.2-standalone-activity/temporal_cli_1.6.2-standalone-activity_darwin_amd64.tar.gz | tar xz

# Linux arm64
curl -L https://github.com/temporalio/cli/releases/download/v1.6.2-standalone-activity/temporal_cli_1.6.2-standalone-activity_linux_arm64.tar.gz | tar xz

# Linux amd64
curl -L https://github.com/temporalio/cli/releases/download/v1.6.2-standalone-activity/temporal_cli_1.6.2-standalone-activity_linux_amd64.tar.gz | tar xz
```

Move the `temporal` binary to somewhere on your PATH, or run it from the current directory with `./temporal`.

Verify:
```bash
./temporal --version
# Expected: temporal version 1.6.2-standalone-activity (Server 1.31.0-151.2, UI 2.47.2)
```

## Quick start (local dev server)

**1. Install dependencies:**
```bash
uv sync
```

**2. Start the dev server** (in a separate terminal):
```bash
./temporal server start-dev
```

The Temporal UI will be available at http://localhost:8233.

**3. Start the worker** (in a separate terminal in the `python` subfolder):
```bash
uv run python worker.py
```

**4. Run the starter:** (in a separate terminal in the `python` subfolder
```bash
uv run python starter.py
```

Expected output:
```
Executing standalone activity...
Result: Hello, World!

Starting standalone activity (non-blocking)...
Activity started with ID: greeting-2
Result: Hi, Temporal!
```

You can also see the activity executions in the Temporal UI at http://localhost:8233.

The same code works against Temporal Cloud - see [Running on Temporal Cloud](#running-on-temporal-cloud) below.

## Keep building with Claude Code

This demo is a starting point. All complex systems emerge from simpler working systems. Now that you have something running, use Claude Code with the Temporal Developer Skill to build on it.

### Install Claude Code

See the [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code/overview) for installation instructions.

### Install the Temporal Developer Skill

```bash
claude plugin marketplace add temporalio/agent-skills
claude plugin install temporal-developer@temporal-marketplace
```

Restart Claude Code after installing. Verify the skill loaded:
```bash
claude plugin list
```

You should see `temporal-developer@temporal-marketplace` listed and enabled.

### Use it

Start Claude Code in this project directory:
```bash
claude
```

The skill activates automatically when you ask about Temporal development. Try prompts like:

- "Add heartbeating to the activity so long-running jobs can report progress"
- "Add a retry policy with exponential backoff"
- "Make the activity accept a list of names and process them in parallel"
- "Add a cancellation handler to the activity"
- "Create a new activity that calls an external API with proper error handling"

The skill provides the agent with Temporal SDK references, determinism rules, common patterns, and gotchas so the generated code follows best practices.

## Key concepts

**Standalone Activities vs. Workflow Activities:**

| | Standalone Activity | Workflow Activity |
|---|---|---|
| Started by | Client directly | Workflow code |
| Parent | None | Workflow execution |
| Use case | Durable jobs, fire-and-forget tasks | Orchestrated multi-step processes |
| Visibility | First-class in Temporal UI | Nested under parent workflow |

**Client API:**

```python
# Start + wait (like calling a function)
result = await client.execute_activity(
    my_activity,
    args=[input],
    id="unique-id",
    task_queue="my-queue",
    start_to_close_timeout=timedelta(seconds=30),
)

# Start without waiting (fire-and-forget, or fetch later)
handle = await client.start_activity(
    my_activity,
    args=[input],
    id="unique-id",
    task_queue="my-queue",
    start_to_close_timeout=timedelta(seconds=30),
)
result = await handle.result()  # fetch when ready
```

## Running on Temporal Cloud

The same demo code works against Temporal Cloud with no code changes. The worker and starter use `ClientConfig.load_client_connect_config()`, which reads connection details from environment variables automatically.

There are two authentication options: mTLS client certificates and API keys. The namespace creation differs slightly depending on which you choose.

### Step 1: Install tcld

[tcld](https://docs.temporal.io/cloud/tcld) is the Temporal Cloud CLI.

```bash
# macOS
brew install temporal/tap/tcld

# Or download from https://docs.temporal.io/cloud/tcld
```

Log in:
```bash
tcld login
```

### Step 2: Create a namespace

Pick **Option A (mTLS)** or **Option B (API key)** below. Replace `<name>` with your name or identifier (e.g., `saa-demo-phil`).

#### Option A: Namespace with mTLS

Generate a CA certificate first, then create the namespace with it:

```bash
mkdir -p certs
tcld gen ca --org temporal -d 1y --ca-cert certs/ca.pem --ca-key certs/ca.key
```

Create the namespace with the CA certificate:
```bash
tcld namespace create \
  --namespace saa-demo-<name> \
  --region us-east-1 \
  --ca-certificate-file certs/ca.pem
```

#### Option B: Namespace with API keys

Create the namespace with API key auth (no certificate needed):
```bash
tcld namespace create \
  --namespace saa-demo-<name> \
  --region us-east-1 \
  --auth-method api_key
```

Then create an API key:
```bash
tcld apikey create \
  --name saa-demo-key \
  --description "Standalone Activities demo" \
  --duration 30d
```

Copy the API key secret from the output - it is only shown once.

#### Verify the namespace

`tcld namespace create` is asynchronous and returns a request ID. Check the status:
```bash
tcld request get --request-id <request-id>
```

Once the request status shows fulfilled, verify the namespace:
```bash
tcld namespace get --namespace saa-demo-<name>.<account_id>
```

Note your **account ID** from the output. Your full namespace name will be `saa-demo-<name>.<account-id>`.

### Step 3: Request Standalone Activities enablement

Standalone Activities is in **Pre-release**. It is not enabled by default on new namespaces.

Contact your Temporal account team to request enablement for your namespace. If you don't have an account team contact, reach out in the [Temporal Community Slack](https://t.mp/slack) `#support` channel.

> **Pre-release limitations:**
> - Not recommended for production workloads
> - Data retention limited to 1 day
> - Delete, pause, reset, and update operations are not yet supported
> - Free for evaluation during Pre-release

### Step 4: Set environment variables and run

#### For mTLS (Option A):
```bash
export TEMPORAL_ADDRESS=saa-demo-<name>.<account-id>.tmprl.cloud:7233
export TEMPORAL_NAMESPACE=saa-demo-<name>.<account-id>
export TEMPORAL_TLS_CLIENT_CERT_PATH=certs/ca.pem
export TEMPORAL_TLS_CLIENT_KEY_PATH=certs/ca.key
```

#### For API keys (Option B):
```bash
export TEMPORAL_ADDRESS=<region>.<cloud-provider>.api.temporal.io:7233
export TEMPORAL_NAMESPACE=saa-demo-<name>.<account-id>
export TEMPORAL_API_KEY=<your-api-key-secret>
```

The address format for API key auth uses the regional API endpoint. For `us-east-1` on AWS:
```
us-east-1.aws.api.temporal.io:7233
```

#### Start the worker and run the starter:
```bash
# Terminal 1
uv run python worker.py

# Terminal 2
uv run python starter.py
```

### Switching between local and Cloud

The code automatically uses the right connection based on which environment variables are set:

| Variable | Local dev | Cloud (mTLS) | Cloud (API key) |
|---|---|---|---|
| `TEMPORAL_ADDRESS` | not set (defaults to `localhost:7233`) | `<ns>.<acct>.tmprl.cloud:7233` | `<region>.<provider>.api.temporal.io:7233` |
| `TEMPORAL_NAMESPACE` | not set (defaults to "default") | `<ns>.<acct>` | `<ns>.<acct>` |
| `TEMPORAL_TLS_CLIENT_CERT_PATH` | not set | path to `ca.pem` | not set |
| `TEMPORAL_TLS_CLIENT_KEY_PATH` | not set | path to `ca.key` | not set |
| `TEMPORAL_API_KEY` | not set | not set | your API key |

To switch back to local development, unset all Temporal environment variables:
```bash
unset TEMPORAL_ADDRESS TEMPORAL_NAMESPACE TEMPORAL_TLS_CLIENT_CERT_PATH TEMPORAL_TLS_CLIENT_KEY_PATH TEMPORAL_API_KEY
```

## Resources

- [Standalone Activities docs](https://docs.temporal.io/standalone-activity)
- [Python SDK standalone activities guide](https://docs.temporal.io/develop/python/standalone-activities)
- [Temporal Cloud namespaces](https://docs.temporal.io/cloud/namespaces)
- [Temporal Cloud certificates](https://docs.temporal.io/cloud/certificates)
- [Temporal Cloud API keys](https://docs.temporal.io/cloud/api-keys)
- [Temporal Developer Skill](https://github.com/temporalio/skill-temporal-developer)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
