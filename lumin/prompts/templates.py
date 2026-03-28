def nl_to_code_prompt(question, schema, sample):
    return f"""
You are a Python data analyst. Given the dataframe schema and sample below,
write a single Python/Pandas expression or short block that answers the question.

STRICT RULES:
- Use 'df' as the variable name.
- Return ONLY the raw executable code. No explanation, no markdown fences, no backticks.
- NEVER use matplotlib, plt, seaborn, or any plotting library.
- NEVER return just 'pd', 'np', or 'df' alone — always return a computed result.
- Your code must return a DataFrame or Series (not a module, not None).
- For time-based questions: parse dates with pd.to_datetime if needed, then groupby date column.
- For relationship/correlation questions: return a DataFrame with both columns.
- For scatter/comparison questions: return df[[col1, col2]] or a grouped aggregation.
- Always use .reset_index() after groupby so the result is a proper DataFrame.
- If you need to parse dates first, do it on a separate line, then write the groupby on the NEXT line as a standalone expression.
- The LAST line of your code must always be a standalone expression that returns a DataFrame or Series — never an assignment.
- NEVER end with df['col'] = ... as the last line. Always end with a query/aggregation that returns data.
- If writing a multi-line block, assign the final answer to a variable called 'result'.

Schema:
{schema}

Sample (5 rows):
{sample}

Question: {question}

Good examples:
- "sales over time" → df.groupby('Date')['Sales'].sum().reset_index()
- "marketing spend vs sales" → df[['Marketing_Spend','Sales']]
- "returns vs sales" → df[['Returns','Sales']]
- "profit margin by product" → df.assign(margin=df['Profit']/df['Sales']).groupby('Product')['margin'].mean().reset_index()
"""


def nl_to_sql_prompt(question, schema, sample):
    return f"""
You are a SQL expert. Given the table schema and sample below,
write a single SQL query that answers the question.
The table name is always 'df'.

STRICT RULES:
- Return ONLY the raw SQL query. No explanation, no markdown fences, no backticks.
- Always use 'df' as the table name.
- Use standard SQL syntax compatible with SQLite.
- Keep it simple and readable.

Schema:
{schema}

Sample (5 rows):
{sample}

Question: {question}

Good examples:
- "total sales by region" → SELECT Region, SUM(Sales) as Total_Sales FROM df GROUP BY Region ORDER BY Total_Sales DESC
- "top 5 products by profit" → SELECT Product, SUM(Profit) as Total_Profit FROM df GROUP BY Product ORDER BY Total_Profit DESC LIMIT 5
- "sales over time" → SELECT Date, SUM(Sales) as Daily_Sales FROM df GROUP BY Date ORDER BY Date
"""


def insight_prompt(question, result, schema):
    return f"""
You are a data analyst. Given the query result below, write 3-5 sentences of 
plain English insight explaining what the data shows.

Schema: {schema}
Question asked: {question}
Result: {result}
"""

def why_what_next_prompt(question, result, schema):
    return f"""
You are a senior data analyst. Given the result below:
1. In 2-3 sentences, explain WHY this pattern or result might have occurred.
2. Suggest exactly 3 specific follow-up questions the user should explore next.
   Format them as a numbered list.

Schema: {schema}
Question: {question}
Result: {result}
"""

def what_if_prompt(column, original_mean, simulated_mean, delta_pct, affected_stats):
    return f"""
A user is simulating a {delta_pct:+.1f}% change in '{column}'.
Original mean: {original_mean:.2f} → Simulated mean: {simulated_mean:.2f}
Affected stats: {affected_stats}

In 2-3 sentences, explain the potential real-world impact of this change.
"""

def anomaly_prompt(column_summary):
    return f"""
The following anomalies were detected in the dataset:
{column_summary}

In 3-5 sentences, explain what these anomalies might indicate in a business context
and what actions should be considered.
"""