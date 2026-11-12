import json
from scripts.summarize_e0020 import prepare


def test_summary_is_descriptive_even_if_seed_diversity_not_validated(tmp_path):
    metadata={"source_blend_sha256":"a"*64, "blender":"5.0.1", "scene_name":"Main", 
              "frame":1,"resolution":[320,240],"samples":16,"extra_input_seeds":[911,1337],
              "seed":539,"reference_samples":384,"second_reference":True}
    ref={"large_reference_discrepancy_alert":True, "convergence_proven":False,
         "reference_disagreement_over_raw_error":0.3}
    report={"reference_quality_diagnostic":ref,"independent_reference_difference":{"rmse_linear":0.01},
            "reference_ranking_consistent":False}
    metrics={"rmse_linear":{"mean":0.05},"mae_linear":{"mean":0.02}}
    agg={"input_diversity_heuristic_passed":False,"sampling_independence_proven":False,
         "rank_by_mean_rmse":None,"rank_by_mean_edge_gradient_rmse":None,
         "methods":{"STANDARD":metrics},
         "detail_methods":{"STANDARD":{"edge_gradient_rmse":{"mean":0.03},
                                       "edge_contrast_ratio":{"mean":1.2}}}}
    for name,data in (("metadata",metadata),("metrics",report),("seed_aggregate",agg)):
        (tmp_path/(name+".json")).write_text(json.dumps(data))
    summary=prepare(tmp_path)
    assert "large discrepancy: **True**" in summary
    assert "convergence proven: **False**" in summary
    assert "Only" not in summary
    assert "| STANDARD | 0.0500000 | 0.0300000 | 1.2000000 | 0.0200000 |" in summary
    assert "n/a" not in summary
