"""The LLM-driven agent loop (ADR-005 / ADR-009).

Unlike the fixed-plan pipeline, the agent decides ONE tool at a time by asking a model,
then runs that tool through the very same safety gates (via StepRunner) before the next
turn. See :mod:`core.agent.loop`.
"""
