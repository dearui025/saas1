# Supabase Edge Functions for AI Trading Bot

This directory contains the Supabase Edge Functions for the AI Trading Bot web interface.

## Functions

1. `web-interface` - Main web interface API
2. `account-info` - Account information API
3. `trading-stats` - Trading statistics API
4. `ai-decisions` - AI decisions API

## Deployment

To deploy these functions to Supabase:

1. Install Supabase CLI
2. Link your project: `supabase link --project-ref your-project-id`
3. Deploy functions: `supabase functions deploy`

## Environment Variables

The following environment variables need to be set in your Supabase project:

- `DEEPSEEK_API_KEY`
- `BINANCE_API_KEY`
- `BINANCE_SECRET`