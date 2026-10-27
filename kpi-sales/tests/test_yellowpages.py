import sys; sys.path.insert(0, ".")
from leadgen import yellowpages as y
H = '<title>AIBADA ZIPPER | YP</title><script type="application/ld+json">{"@graph":[{"@type":"LocalBusiness","name":"AIBADA ZIPPER OOO","telephone":"95 1578880","email":"a@b.uz"}]}</script>'
def test_parse():
    r = y.parse(H, "u"); assert r["phone"] == "998951578880" and r["name"].startswith("AIBADA")
