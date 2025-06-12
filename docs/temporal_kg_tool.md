# Temporal Knowledge Graph Tool

The Temporal Knowledge Graph Tool (`temporal_kg_search`) is an intelligent tool designed to answer time-sensitive questions about customer events and timelines using a Neo4j graph database.

## Overview

This tool uses advanced LLM-based query parsing with robust fallback mechanisms to understand natural language queries about customer events, generate appropriate Cypher queries, and format results in human-readable formats.

## Features

### 🧠 **Intelligent Query Parsing**
- **LLM-powered**: Uses advanced language models to understand complex temporal queries
- **Fallback parsing**: Robust regex-based parsing when LLM is unavailable
- **Natural language mapping**: Converts phrases like "signed up" → "Signup", "bought" → "Purchase"

### 📊 **Query Types Supported**

1. **Single Event Queries**
   - "When did CUST001 make their first purchase?"
   - "Show me CUST002's last login"

2. **Timeline Queries**
   - "Show me the complete timeline for CUST003"
   - "List all events for CUST001 in chronological order"

3. **Comparison Queries**
   - "Who signed up first, CUST001 or CUST002?"
   - "Compare the upgrade dates of CUST001 and CUST003"

4. **Event Sequence Analysis**
   - "What happened to CUST002 after their support ticket was resolved?"
   - "Show me CUST003's events leading up to cancellation"

### 🎯 **Smart Result Formatting**
- **Single events**: Customer name, event type, timestamp, and relevant details
- **Comparisons**: Ranked lists with timestamps
- **Timelines**: Chronological event sequences with full context

## Supported Event Types

- **Signup** (with plan type)
- **Upgrade** (with from/to plans)
- **Login** (with timestamp)
- **Purchase** (with date and details)
- **SupportTicket** (with creation date)
- **TicketResolved** (with resolution date)
- **Cancellation** (with date)

## Available Customer Data

- **CUST001**: Success story (signup → upgrade → purchase)
- **CUST002**: Support-driven journey (signup → support ticket → resolution)
- **CUST003**: Churn scenario (signup → usage → cancellation)

## Usage Examples

### Single Event Queries 