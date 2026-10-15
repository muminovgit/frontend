import sys; sys.path.insert(0, ".")
from leadgen import pipeline, phones, sectors

def test_all():
    L = pipeline.enrich(pipeline.load_csv("data/sample_leads.csv"))
    assert len(L) == 4                                  # dedupe by STIR
    assert L[0]["sector"] in ("manufacturing", "security")
    assert phones.normalize("+998 90 123 45 67") == "998901234567"
    assert not phones.is_mobile("998712345678")         # landline excluded
    q = pipeline.sms_queue(L, min_score=0)
    assert all(p.startswith("99890") or p[3:5] in phones.MOBILE for p, _ in q) and len(q) == 3 and "998712345678" not in [p for p, _ in q]
    assert pipeline.sms_queue(L, 0, optouts={"998901234567"}).__len__() == 2
    assert sectors.classify("xyz") == "other"
