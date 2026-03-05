# Deploying to Railway

Step-by-step guide for deploying the Author Factsheet Review app to [Railway](https://railway.app) using the Railway CLI.

## Prerequisites

- [Railway CLI](https://docs.railway.app/guides/cli) installed (`npm install -g @railway/cli` or `brew install railway`)
- A Railway account (free tier works)
- Python 3 available locally (for generating the secret key)

Verify the CLI is installed:

```bash
railway --version
```

## Step 1: Login

```bash
railway login
```

This opens a browser window to authenticate.

## Step 2: Create a New Project

```bash
railway init
```

When prompted, give it a name like `author-factsheet-review`.

## Step 3: Add PostgreSQL

```bash
railway add --database postgres
```

This provisions a managed PostgreSQL instance attached to your project.

## Step 4: Link the Service

Navigate to the app directory and link it to the Railway project:

```bash
cd apps/author_review
railway link
```

Select the project you created in Step 2.

## Step 5: Set Environment Variables

```bash
railway variables set ADMIN_PASSWORD="your-strong-password-here"
```

Set `DATABASE_URL` using the public URL from the Postgres service. Run `railway variables` to find `DATABASE_PUBLIC_URL`, then copy that value:

```bash
railway variables set DATABASE_URL="postgresql://postgres:PASSWORD@HOST:PORT/railway"
```

> **Warning (Windows CMD):** Do **not** use `${{Postgres.DATABASE_URL}}` syntax from CMD — it will corrupt the value. Either use the Railway web dashboard to add a reference variable, or copy the actual Postgres URL as shown above.

Generate a secret key and set it (two separate commands on Windows CMD):

```bash
# First, generate a key:
python -c "import secrets; print(secrets.token_hex(32))"

# Then copy the output and set it:
railway variables set SECRET_KEY="paste-the-hex-string-here"
```

On bash/macOS/Linux you can do it in one line:

```bash
railway variables set SECRET_KEY="$(python -c "import secrets; print(secrets.token_hex(32))")"
```

> **Note:** `BASE_URL` is set after the first deploy once you have a public domain (see Step 7).

## Step 6: Deploy

```bash
railway up
```

This pushes the `apps/author_review` directory to Railway and builds it using the Dockerfile. The first deploy takes a few minutes.

## Step 7: Generate a Public Domain and Set BASE_URL

```bash
railway domain
```

This generates a `*.up.railway.app` URL. Copy it and set the `BASE_URL` variable:

```bash
railway variables set BASE_URL="https://your-generated-domain.up.railway.app"
```

Replace `your-generated-domain` with the actual domain from the previous command. Do **not** include a trailing slash.

This triggers a redeploy automatically.

## Step 8: Verify

Open the app in your browser:

```bash
railway open
```

Then check:

- `/health` — should return `{"status": "ok"}`
- `/admin/login` — log in with the `ADMIN_PASSWORD` you set in Step 5
- Search for an author, generate a review token, and test the review flow

## Redeploying

After making code changes locally, redeploy with:

```bash
cd apps/author_review
railway up
```

Or connect a GitHub repo in the Railway dashboard for automatic deploys on push.

## Viewing Logs

```bash
railway logs
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `railway status` | Show current project and service info |
| `railway variables` | List all environment variables |
| `railway logs` | Stream live logs |
| `railway open` | Open the app in your browser |
| `railway domain` | Show or generate the public domain |
| `railway down` | Take the deployment offline |

## Resetting the Database on Railway

Connect to the Railway PostgreSQL instance and drop/recreate the schema:

```bash
railway connect postgres
```

Then in the psql shell:

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
```

Restart the service (tables are recreated automatically on startup):

```bash
railway up
```
