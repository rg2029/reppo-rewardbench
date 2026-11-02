"""Static-first HF Space. Explicitly does not call a paid API."""
import json
import os
# Spaces enables SSR by default; disable its Node proxy for this static viewer.
os.environ["GRADIO_SSR_MODE"] = "False"
import gradio as gr

INTRO = """# Reppo RewardBench
**Can independent economic feedback improve reinforcement learning?**

This is a **research scaffolding and results-audit viewer**. No validated
research scores have yet been released. A reward-quality improvement would not
by itself establish improved learning; that requires downstream evaluation.

- **Track A:** independently verified reward ranking (primary: task-macro pairwise accuracy).
- **Track B:** economic weighting vs. uniform aggregation using identical peer inputs.
- **Track C:** frozen-policy best-of-N and, separately, true online RL if weights are updated.

Every score must include raw provenance, a held-out split, matched baselines,
uncertainty intervals and missingness reporting.
"""


def inspect_report(file):
    if file is None:
        return 'No report selected.', []
    try:
        with open(getattr(file, "name", file), encoding='utf-8') as fh:
            obj = json.load(fh)
        report = obj.get('study', obj)
        methods = report.get('methods', {})
        lines = []
        for name, stats in sorted(methods.items()):
            lines.append([name, stats.get('tasks_complete'), stats.get('tasks_expected'),
                          stats.get('macro_task_pairwise_accuracy'), ', '.join(stats.get('source_types', []))])
        caveat = report.get('scientific_evidence', 'Unspecified evidence status: do not use for claims.')
        if report.get('simulation_present', False) or report.get('split') == 'smoke':
            caveat = 'DEMONSTRATION ONLY — synthetic/smoke data, not scientific evidence. ' + caveat
        return caveat, lines
    except Exception as exc:
        return 'Invalid report: ' + str(exc), []


with gr.Blocks(title='Reppo RewardBench') as demo:
    gr.Markdown(INTRO)
    with gr.Row():
        uploader = gr.File(label='Load a benchmark report.json (local analysis only)', file_types=['.json'])
    summary = gr.Textbox(label='Evidence status', value='No empirical results published.', interactive=False)
    table = gr.Dataframe(headers=['Method', 'Complete tasks', 'Expected tasks', 'Task-macro pairwise accuracy', 'Data provenance'],
                         datatype=['str', 'number', 'number', 'number', 'str'], interactive=False)
    uploader.change(fn=inspect_report, inputs=uploader, outputs=[summary, table])
    gr.Markdown('**Important:** This demo does not verify uploaded reports, call Reppo or upload files to a research server. Confirm independent task labels and candidate provenance before citing any result.')

if __name__ == '__main__':
    demo.launch(ssr_mode=False, show_error=True)
