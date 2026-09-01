# LLMPrint frozen validation-negative panel

The Experiment A/Ba panel is frozen at 13/13 official identities, with no replacements and no unresolved slots. ModelScope is transport only. Each entry uses the exact upstream owner/repository ID and a pinned ModelScope Git revision. OpenAPI metadata plus revision-pinned `config.json` establish matching causal-LM architecture, dimensions, vocabulary, base/instruct role, ordinary PyTorch/Safetensors weights, and no quantization/LoRA/merge indication. This is recorded as `scientifically_equivalent_transport_mirror`, not byte identity; acquisition must still verify files and tensors where feasible.

| Slot | Official and ModelScope ID | Frozen ModelScope revision | Architecture / scale | Role | Verdict |
|---:|---|---|---|---|---|
| 1 | `bigscience/bloom-560m` | `67fb84cb53be712b3e92e45cba9521ce27f045cc` | BLOOM / 559M | base | exact identity mirror |
| 2 | `distilbert/distilgpt2` | `0fb7dd952af471c396cbfee653bef1e8de6a8fc7` | GPT-2 / 88M | distilled base | exact identity mirror |
| 3 | `facebook/opt-1.3b` | `f6a448dd64ab9aabcd5bd90e2ea54735cef08400` | OPT / 1.3B | base | exact identity mirror |
| 4 | `facebook/opt-350m` | `b42169562a1c400487e9b3174db76504225929de` | OPT / 350M | base | exact identity mirror |
| 5 | `google/gemma-2b` | `4c0ad9bd274f4fda9be830b72a0833fb1f74a12e` | Gemma / 2.51B | base | exact identity mirror |
| 6 | `google/gemma-3-1b-it` | `e7f7ff0c49b3ab4e78e82856925a0327d8c780ab` | Gemma 3 / 1B | instruct | exact identity mirror |
| 7 | `microsoft/phi-2` | `1650c3d781609187dc5133d1baf8fdf2921b874b` | Phi / 2.78B | base | exact identity mirror |
| 8 | `microsoft/Phi-3-mini-128k-instruct` | `36dd6bdc2b730342af51ce16740601d6471e73ff` | Phi-3 / 3.82B | instruct | exact identity mirror |
| 9 | `openai-community/gpt2` | `9ab344760a7f8baa164ea1d3cbfc3849997b070f` | GPT-2 / 137M | base | exact identity mirror |
| 10 | `Qwen/Qwen2-7B` | `96127251daf38ea8aa588eac3d34faf64682c0e5` | Qwen2 / 7.62B | base | exact identity mirror |
| 11 | `Qwen/Qwen2.5-3B-Instruct` | `8f4992eda43eea7c770690ddc0de8f732da246f5` | Qwen2 / 3.09B | instruct | exact identity mirror |
| 12 | `Qwen/Qwen2.5-7B-Instruct` | `16c174980d8a1492910551634b4969e69cdc2444` | Qwen2 / 7.62B | instruct | exact identity mirror |
| 13 | `tiiuae/Falcon3-7B-Base` | `5381fafb1daa3aa44232effce105b71f7925b6c3` | Falcon3/Llama / 7.46B | base | exact identity mirror |

No replacement is approved or needed. The panel preserves BLOOM, GPT-2, OPT, Gemma, Phi, Qwen, and Falcon families across roughly 88M–7.62B parameters. None is derived from the canonical Llama-3.2-3B-Instruct Reference.
