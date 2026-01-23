# Iteration Status Email Notifications Setup

This guide explains how to configure and use the automated iteration status email notification system for Symphonic-Joules.

## Overview

The iteration status email notification system automatically parses the progress dashboard and sends daily status updates to team leads. It identifies tasks that are:
- 🏃 **In Progress** (`:runner:`) - Tasks actively being worked on
- ✋ **Blocked/Needs Review** (`:hand:`) - Tasks waiting for attention or blocked

## How It Works

The GitHub Actions workflow (`iteration-status-emails.yml`) performs the following:

1. **Triggers** on:
   - Updates to `docs/january-2026-progress.md` (or similar dashboard files)
   - Daily schedule at 9:00 AM UTC
   - Manual workflow dispatch for testing

2. **Parses** the dashboard file to extract:
   - Tasks marked with 🏃 or `:runner:` (in progress)
   - Tasks marked with ✋ or `:hand:` (blocked/needs review)

3. **Sends** an email notification to configured team leads with:
   - Count of in-progress tasks
   - Count of blocked tasks
   - Full list of task details
   - Link to the full dashboard

## Required GitHub Secrets

To use this workflow, you must configure the following secrets in your GitHub repository:

### Navigate to Repository Settings
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

### Required Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` (for TLS) or `465` (for SSL) |
| `SMTP_USERNAME` | SMTP authentication username | `notifications@yourcompany.com` |
| `SMTP_PASSWORD` | SMTP authentication password or app password | `your-secure-password` |
| `SENDER_EMAIL` | Email address to send from | `symphonic-bot@yourcompany.com` |
| `TEAM_LEADS_EMAIL` | Comma-separated list of recipient emails | `meganrogge@example.com,anthonykim1@example.com` |

### Common SMTP Provider Settings

#### Gmail
- **SMTP_SERVER:** `smtp.gmail.com`
- **SMTP_PORT:** `587`
- **Note:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular Gmail password

#### Microsoft 365 / Outlook
- **SMTP_SERVER:** `smtp.office365.com`
- **SMTP_PORT:** `587`

#### SendGrid
- **SMTP_SERVER:** `smtp.sendgrid.net`
- **SMTP_PORT:** `587`
- **SMTP_USERNAME:** `apikey`
- **SMTP_PASSWORD:** Your SendGrid API key

#### Amazon SES
- **SMTP_SERVER:** `email-smtp.us-east-1.amazonaws.com` (adjust region)
- **SMTP_PORT:** `587`

## Dashboard Format

The workflow parses markdown files looking for specific emoji indicators. Ensure your dashboard follows this format:

### Example Task Format

```markdown
## Week 1 Tasks

### Core Features
- ✅ Completed task
- 🏃 Task in progress - @assignee (this will be detected)
- ✋ Blocked task - @assignee (this will be detected)
- 📋 Planned task

### Documentation
- 🏃 API documentation - @contributor (this will be detected)
- ✋ Review needed for setup guide - @reviewer (this will be detected)
```

### Supported Emoji Formats

Both Unicode emoji and GitHub shortcodes are supported:

- In Progress: `🏃` or `:runner:`
- Blocked: `✋` or `:hand:`

### Important Format Requirements

For the parsing to work correctly, tasks **must** follow this exact format:

```markdown
- 🏃 Task description - @assignee
- ✋ Another task - @assignee (optional notes)
```

**Critical formatting rules:**
1. Start with a dash and space: `- `
2. Followed by the emoji and space: `🏃 ` or `✋ `
3. Then the task description
4. Do NOT use parentheses immediately after the emoji (e.g., `🏃 (text)` will be filtered out as a legend entry)
5. Avoid using the emoji in headers (`##`) or legend sections

The workflow filters out:
- Markdown headers containing emoji
- Legend entries (lines with emoji followed by parentheses)
- Summary statistics containing emoji

## Testing the Workflow

### Manual Trigger (Recommended for Testing)

1. Go to **Actions** tab in GitHub
2. Select **Iteration Status Email Updates** workflow
3. Click **Run workflow** → **Run workflow**
4. Check the workflow run logs to verify parsing and email sending

### Test with Dashboard Update

1. Update `docs/january-2026-progress.md`
2. Add or modify tasks with 🏃 or ✋ emoji
3. Commit and push changes
4. Workflow will trigger automatically

### Verify Email Receipt

After triggering the workflow:
1. Check the configured email addresses for the notification
2. Verify that task counts are accurate
3. Confirm that task details are properly formatted

## Troubleshooting

### Email Not Received

**Check Secrets Configuration:**
```bash
# Verify secrets are set (shows names only, not values)
# Navigate to: Settings → Secrets and variables → Actions
```

**Common Issues:**
- Incorrect SMTP server address or port
- Invalid credentials (username/password)
- Firewall blocking SMTP connections
- Email caught in spam filter

### Parsing Issues

**Verify Dashboard Format:**
- Ensure emoji are properly formatted (🏃 or `:runner:`)
- Check that the dashboard file path matches the workflow configuration
- Verify the file exists at `docs/january-2026-progress.md`

### Workflow Failures

1. Go to **Actions** tab
2. Click on the failed workflow run
3. Expand the failed step to view detailed logs
4. Common failure points:
   - **Checkout** - repository access issues
   - **Parse dashboard** - file not found or parsing errors
   - **Send email** - SMTP configuration or authentication issues

## Customization

### Change Schedule

Edit `.github/workflows/iteration-status-emails.yml`:

```yaml
schedule:
  # Run at different time (e.g., 5 PM UTC)
  - cron: '0 17 * * *'
  
  # Run twice daily (9 AM and 5 PM UTC)
  - cron: '0 9,17 * * *'
  
  # Run only on weekdays (Monday-Friday)
  - cron: '0 9 * * 1-5'
```

### Change Dashboard File

Update the workflow to monitor different files:

```yaml
paths:
  - 'docs/january-2026-progress.md'
  - 'docs/february-2026-progress.md'  # Add more paths
```

### Add Additional Recipients

Update the `TEAM_LEADS_EMAIL` secret with comma-separated addresses:
```
lead1@example.com,lead2@example.com,lead3@example.com
```

### Attach Dashboard File

Uncomment the attachments line in the workflow:

```yaml
attachments: docs/january-2026-progress.md
```

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Use app-specific passwords** when available (Gmail, Outlook)
3. **Rotate credentials** regularly
4. **Limit email account permissions** to sending only
5. **Use dedicated service accounts** for automated emails
6. **Enable 2FA** on email accounts where possible

## Email Content Example

```
Subject: [Symphonic-Joules] Daily Iteration Status - 2026-01-22

Hello Team Leads,

This is your daily iteration status update for Symphonic-Joules.

=== IN PROGRESS TASKS (🏃) ===
Count: 3

15: - 🏃 Audio processing framework implementation - @contributor1
16: - 🏃 API reference documentation - @contributor3
25: - 🏃 Unit test coverage for audio module - @contributor1

=== BLOCKED/NEEDS REVIEW TASKS (✋) ===
Count: 1

17: - ✋ Energy calculation module design - @contributor2 (blocked on physics validation)

=== SUMMARY ===
- Tasks in progress: 3
- Tasks blocked/needing review: 1

View full dashboard: https://github.com/JaclynCodes/Symphonic-Joules/blob/main/docs/january-2026-progress.md

---
Automated notification from Symphonic-Joules Iteration Status System
```

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review workflow logs in the Actions tab
3. Create an issue in the repository with:
   - Description of the problem
   - Relevant workflow logs
   - Dashboard file content (if applicable)
   - Non-sensitive configuration details

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cron Expression Syntax](https://crontab.guru/)
- [action-send-mail Documentation](https://github.com/dawidd6/action-send-mail)
