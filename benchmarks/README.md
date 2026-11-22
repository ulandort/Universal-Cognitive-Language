# UCLBench — automated offline benchmark (development)

No AI API keys, network, or paid services needed. This deterministic suite verifies mechanics of the existing UCL/1.0 implementation and experimental 2.0 guide profile wrapper. It runs on GitHub Actions.

```sh
python benchmarks/offline_suite.py --iterations 1000 --seed 2026 --out uclbench-results.json
python -m unittest discover -s benchmarks -p 'test_*.py' -v
```

Machine-readable JSON records a seed, test count, failures, and canonical packet sizes. Each test checks a known invariant; no AI reasoning or comprehension is inferred. To reproduce a failure, run with the same seed and iterations. The test corpus includes the actual 13-act Grok–Qwen synthetic/externally-authored experiment packet.

This suite is not a comparison with English or structured English. Future live-model benchmarks must be separately labeled and must measure the full cost of prompts, encoders, validators and fallbacks.